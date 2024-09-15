import requests
import json
from config import config
from utils import construct_compare_url, construct_comments_url, construct_comment_url

def verify_repo_access(repository):
    """
    Verifies if the GitHub token has access to the specified repository.

    Args:
        repository (str): The full name of the repository (e.g., owner/repo).

    Returns:
        bool: True if access is verified, False otherwise.
    """
    if config.TEST_MODE:
        print(f"TEST_MODE: Skipping repository access verification for '{repository}'.")
        return True
    repo_url = f"https://api.github.com/repos/{repository}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {config.GITHUB_ACCESS_TOKEN}'
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
    if config.TEST_MODE:
        print("TEST_MODE: Skipping retrieval of bot comment ID.")
        return None

    comments_url = construct_comments_url(repository_full_name, pr_number)
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {config.GITHUB_ACCESS_TOKEN}'
    }

    try:
        response = requests.get(comments_url, headers=headers)
        response.raise_for_status()
        comments = response.json()
        
        print("Checking comments to see if the bot has already commented.")
        for comment in comments:
            comment_body = comment.get('body', '')
            if 'Automated Code Review' in comment_body:
                print("Bot has already commented on this PR.")
                return comment.get('id')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve comments: {e}")
        return None

def post_or_update_comment(repository_full_name, pr_number, review_content, comment_id, github_token, test_mode):
    """
    Posts a new comment or updates an existing comment on the PR.

    Args:
        repository_full_name (str): The full name of the repository (e.g., owner/repo).
        pr_number (int): The number of the pull request.
        review_content (str): The content of the review.
        comment_id (int or None): The ID of the existing comment if any.
        github_token (str): GitHub access token.
        test_mode (bool): Flag to indicate if it is in test mode.

    Returns:
        None
    """
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {github_token}'
    }

    if test_mode:
        print("TEST_MODE: Skipping posting comments to GitHub.")
        print(f"Review content:\n{review_content}")
        return

    if comment_id:
        # Update the existing comment
        comment_url = construct_comment_url(repository_full_name, comment_id)
        comment_body = {
            "body": f"**EXPERIMENTAL: Automated Code Review (Updated)**\n\n{review_content}"
        }
        try:
            update_response = requests.patch(comment_url, headers=headers, data=json.dumps(comment_body))
            update_response.raise_for_status()
            print(f"Updated comment on PR #{pr_number}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to update comment: {e}")
    else:
        # Post a new comment
        comments_url = construct_comments_url(repository_full_name, pr_number)
        comment_body = {
            "body": f"**EXPERIMENTAL: Automated Code Review**\n\n{review_content}"
        }
        try:
            comment_response = requests.post(comments_url, headers=headers, data=json.dumps(comment_body))
            comment_response.raise_for_status()
            print(f"Comment posted successfully to PR #{pr_number}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to post comment: {e}")
