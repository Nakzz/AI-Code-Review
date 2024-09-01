import json
from config import config
from openai_client import ReviewResponse, review_code_with_openai
from github_client import (
    verify_repo_access,
    get_bot_comment_id,
    post_or_update_comment
)
from utils import get_changeset, parse_event_body

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
    body = parse_event_body(event)

    pr_event = body.get('action', 'Unknown')
    pr_details = body.get('pull_request', {})
    pr_title = pr_details.get('title', 'No Title')
    pr_number = pr_details.get('number', 'Unknown')
    pr_description = pr_details.get('body', 'No Description')
    repository_info = body.get('repository', {})
    repository_full_name = repository_info.get('full_name', 'Unknown')
    base_branch = pr_details.get('base', {}).get('ref', 'Unknown')
    head_branch = pr_details.get('head', {}).get('ref', 'Unknown')

    print(f"Pull Request #{pr_number} - {pr_title} - Action: {pr_event}")
    print(f"Repository: {repository_full_name}")
    print(f"Base branch: {base_branch}, Head branch: {head_branch}")

    # Verify repository access
    if not config.TEST_MODE and not verify_repo_access(repository_full_name):
        return {
            'statusCode': 403,
            'body': json.dumps(f"API key does not have access to the repository: {repository_full_name}")
        }
    
    if config.TEST_MODE:
        comment_id = None
    else:
        comment_id = get_bot_comment_id(pr_number, repository_full_name)

    if config.TEST_MODE:
        # Use full_context from context if available
        if hasattr(context, 'full_context'):
            full_context = context.full_context
            print("Using provided full_context from test_main.py.")
        else:
            full_context = "Stubbed changeset for testing."
            print("Using default stubbed changeset for testing.")

    try:
        # Get the changeset
        full_context = full_context or get_changeset(repository_full_name, base_branch, head_branch, config.GITHUB_ACCESS_TOKEN)
        openai_review: ReviewResponse = review_code_with_openai(full_context, pr_title, pr_description)

        if openai_review is not None:            
            post_or_update_comment(
                repository_full_name,
                pr_number,
                openai_review.pull_request_description +"\n" +openai_review.feedback,
                comment_id,
                config.GITHUB_ACCESS_TOKEN,
                config.TEST_MODE
            )
              
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {e}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps(f'GitHub PR webhook processed: {pr_event}')
    }
