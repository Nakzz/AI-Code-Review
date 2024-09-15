import json
import requests

def parse_event_body(event):
    """
    Parses the JSON body from the event.

    Args:
        event (dict): The event payload.

    Returns:
        dict: Parsed JSON body.
    """
    return json.loads(event.get('body', '{}'))

def construct_compare_url(repository_full_name, base_branch, head_branch):
    """
    Constructs the GitHub compare URL.

    Args:
        repository_full_name (str): Full name of the repository.
        base_branch (str): The base branch name.
        head_branch (str): The head branch name.

    Returns:
        str: The compare URL.
    """
    return f"https://api.github.com/repos/{repository_full_name}/compare/{base_branch}...{head_branch}"

def construct_comments_url(repository_full_name, pr_number):
    """
    Constructs the GitHub comments URL for a PR.

    Args:
        repository_full_name (str): Full name of the repository.
        pr_number (int): Pull request number.

    Returns:
        str: The comments URL.
    """
    return f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/comments"

def construct_comment_url(repository_full_name, comment_id):
    """
    Constructs the GitHub URL for a specific comment.

    Args:
        repository_full_name (str): Full name of the repository.
        comment_id (int): Comment ID.

    Returns:
        str: The comment URL.
    """
    return f"https://api.github.com/repos/{repository_full_name}/issues/comments/{comment_id}"

def get_changeset(repository_full_name, base_branch, head_branch, github_token):
    """
    Retrieves the changeset between two branches.

    Args:
        repository_full_name (str): Full name of the repository.
        base_branch (str): The base branch name.
        head_branch (str): The head branch name.
        github_token (str): GitHub access token.

    Returns:
        str: The formatted changeset.
    """
    compare_url = construct_compare_url(repository_full_name, base_branch, head_branch)
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {github_token}'
    }

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
    return full_context
