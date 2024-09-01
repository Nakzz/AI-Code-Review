import json
from main import lambda_handler, TEST_MODE

class MockContext:
    def __init__(self, full_context):
        self.full_context = full_context

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
    
    # Define stubbed changeset for testing
    stubbed_changeset = """
    File: example.py
    Changes:
    + def new_function():
    +     pass
    """

    # Create a mock context with full_context
    context = MockContext(full_context=stubbed_changeset)

    # Call the lambda_handler function with the mock context
    lambda_handler(event, context)
