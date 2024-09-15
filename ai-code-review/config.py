import os

# Configuration and constants
class Config:
    def __init__(self):
        self.GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.TEST_MODE = os.getenv("TEST_MODE", "False") == "True"

# Singleton instance
config = Config()
