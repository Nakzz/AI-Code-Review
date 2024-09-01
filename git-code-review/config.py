# Configuration and constants

# TODO: Move sensitive information to environment variables

class Config:
    def __init__(self):
        self.GITHUB_ACCESS_TOKEN = "REMOVED_GITHUB_TOKEN"
        self.OPENAI_API_KEY = "REMOVED_OPENAI_API_KEY"
        self.TEST_MODE = False

# Singleton instance
config = Config()
