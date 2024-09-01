import json
import requests
import openai

# TODO: move to env var
GITHUB_ACCESS_TOKEN = "REMOVED_GITHUB_TOKEN"
OPENAI_API_KEY = "REMOVED_OPENAI_API_KEY"

openai.api_key = OPENAI_API_KEY

# Set TEST_MODE to True when testing locally
TEST_MODE = False

def review_code_with_openai(changeset, pr_title, pr_description):
    """
    Sends the code changeset to OpenAI's API for code review.

    Args:
        changeset (str): The git diff of code changes.
        pr_title (str): The title of the pull request.
        pr_description (str): The description/body of the pull request.

    Returns:
        str: The code review feedback from OpenAI.
    """
    prompt = (
        "You are an experienced software engineer familiar with leading tech practices in security, observability, reliability, object-oriented design, functional programming, and performance.\n"
        "Review the following git diff, focusing only on the new code added. "
        "Provide concise feedback on logic errors or general mistakes to promote better code quality, consistent variable naming, strongly typed(when applicable) and RESTful design(when applicable). Keep those explanations brief, assuming the reader prefers short text and opt."
        "Offer code changes if needed but avoid commenting on acceptable code. "
        "If there are no improvements to suggest, provide an encouraging message to the developer. Creatively be their coding hypeman using modern-day references and jokes!\n"
        "If the Pull Request Description is missing or unknown, summarize the changes by reviewing the code and include a 'Pull Request Description' section in your review. \n"
        "Avoid commenting about the following. - Using a logging library. \n\n\n"
        f"Pull Request Title: {pr_title}\n\n"
        f"Pull Request Description:\n{pr_description}\n\n"
        f"### Code Changes Begin:\n{changeset} \n ### Code Changes Ends"
    )
    
    
    try:
        response = openai.ChatCompletion.create(
            model="o1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000
        )
        review = response.choices[0].message.content.strip()
        print("Code review from OpenAI:\n", review)
        return review
    except openai.error.OpenAIError as e:
        print(f"Failed to get a response from OpenAI: {e}")
        return None
        
def verify_repo_access(repository):
    """
    Verifies if the GitHub token has access to the specified repository.

    Args:
        repository (str): The full name of the repository (e.g., owner/repo).

    Returns:
        bool: True if access is verified, False otherwise.
    """
    if TEST_MODE:
        print(f"TEST_MODE: Skipping repository access verification for '{repository}'.")
        return True
    repo_url = f"https://api.github.com/repos/{repository}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {GITHUB_ACCESS_TOKEN}'
    }
    try:
        response = requests.get(repo_url, headers=headers)
        response.raise_for_status()
        print(f"Access to repository '{repository}' is verified.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to access repository '{repository}': {e}")
        return False

def get_bot_comment_id(pr_number, repository_full_name):
    """
    Retrieves the comment ID if the bot has already commented on the PR.

    Args:
        pr_number (int): The number of the pull request.
        repository_full_name (str): The full name of the repository (e.g., owner/repo).

    Returns:
        int or None: The comment ID if the bot has commented, otherwise None.
    """
    if TEST_MODE:
        print("TEST_MODE: Skipping retrieval of bot comment ID.")
        return None

    comments_url = f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/comments"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {GITHUB_ACCESS_TOKEN}'
    }

    try:
        response = requests.get(comments_url, headers=headers)
        response.raise_for_status()
        comments = response.json()
        
        print("Checking comments to see if the bot has already commented.")
        for comment in comments:
            user_login = comment.get('user', {}).get('login', '')
            comment_body = comment.get('body', '')
            if 'Automated Code Review' in comment_body:
                print("Bot has already commented on this PR.")
                return comment.get('id')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve comments: {e}")
        return None


def lambda_handler(event, context):
    """
    AWS Lambda handler for processing GitHub pull request events.

    Args:
        event (dict): The event payload.
        context (LambdaContext): The runtime information.

    Returns:
        dict: The response dictionary.
    """
    # Parse the body of the event
    body = json.loads(event.get('body', '{}'))
    print(body)
    
    pr_event = body.get('action', 'Unknown')
    pr_details = body.get('pull_request', {})
    pr_title = pr_details.get('title', 'No Title')
    pr_number = pr_details.get('number', 'Unknown')
    pr_description = pr_details.get('body', 'No Description')
    repository_info = body.get('repository', {})
    repository_name = repository_info.get('name', 'Unknown')
    repository_full_name = repository_info.get('full_name', 'Unknown')
    base_branch = pr_details.get('base', {}).get('ref', 'Unknown')
    head_branch = pr_details.get('head', {}).get('ref', 'Unknown')

    print(f"Pull Request #{pr_number} - {pr_title} - Action: {pr_event}")
    print(f"Repository: {repository_full_name}")
    print(f"Base branch: {base_branch}, Head branch: {head_branch}")

    # Verify repository access
    if not verify_repo_access(repository_full_name):
        return {
            'statusCode': 403,
            'body': json.dumps(f"API key does not have access to the repository: {repository_full_name}")
        }
    
    comment_id = get_bot_comment_id(pr_number, repository_full_name)

    if TEST_MODE:
        # Use stubbed changeset data
        full_context = "Stubbed changeset for testing."
    else:
        # Construct the compare URL
        compare_url = f"https://api.github.com/repos/{repository_full_name}/compare/{base_branch}...{head_branch}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {GITHUB_ACCESS_TOKEN}'
        }

        print(f"Comparing changes between {base_branch} and {head_branch} using: {compare_url}")

        try:
            response = requests.get(compare_url, headers=headers)
            response.raise_for_status()
            comparison = response.json()
            changeset = []
            for file in comparison.get('files', []):
                filename = file.get('filename', 'Unknown file')
                patch = file.get('patch', '')
                changeset.append(f"File: {filename}\nChanges:\n{patch}\n")
            changeset_text = "\n".join(changeset)

            # Include commit messages for additional context
            commits = comparison.get('commits', [])
            commit_messages = "\n".join([commit.get('commit', {}).get('message', '') for commit in commits])

            # Combine all context
            full_context = f"{changeset_text}\nCommit Messages:\n{commit_messages}"

            openai_review = review_code_with_openai(full_context, pr_title, pr_description)

            if openai_review:
                if TEST_MODE:
                    print("TEST_MODE: Skipping posting comments to GitHub.")
                    print(f"Review content:\n{openai_review}")
                else:
                    if comment_id:
                        # Update the existing comment
                        comment_url = f"https://api.github.com/repos/{repository_full_name}/issues/comments/{comment_id}"
                        comment_body = {
                            "body": f"**EXPERIMENTAL: Automated Code Review (Updated)**\n\n{openai_review}"
                        }
                        update_response = requests.patch(comment_url, headers=headers, data=json.dumps(comment_body))
                        update_response.raise_for_status()
                        print(f"Updated comment on PR #{pr_number}")
                    else:
                        # Post a new comment
                        comment_url = f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/comments"
                        comment_body = {
                            "body": f"**EXPERIMENTAL: Automated Code Review**\n\n{openai_review}"
                        }
                        comment_response = requests.post(comment_url, headers=headers, data=json.dumps(comment_body))
                        comment_response.raise_for_status()
                        print(f"Comment posted successfully to PR #{pr_number}")
            else:
                print("No review was generated by OpenAI.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"An error occurred: {e}")
            }

    return {
        'statusCode': 200,
        'body': json.dumps(f'GitHub PR webhook processed: {pr_event}')
    }
