import json
from main import lambda_handler, TEST_MODE

if __name__ == '__main__':
    # Enable test mode
    TEST_MODE = True

    # Stub event data for testing
    event = {
        'body': json.dumps({
            'action': 'opened',
            'pull_request': {
                'title': 'Sample Pull Request Title',
                'number': 1,
                'body': 'Sample Pull Request Description',
                'base': {
                    'ref': 'main'
                },
                'head': {
                    'ref': 'feature-branch'
                }
            },
            'repository': {
                'name': 'sample-repo',
                'full_name': 'user/sample-repo'
            }
        })
    }
    # Stub context if needed
    context = None

    # Call the lambda_handler function
    lambda_handler(event, context)
