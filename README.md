# Git Code Review

## Description
This project is an automated code review tool that integrates with GitHub and uses OpenAI's API to provide feedback on pull requests. It analyzes code changes, generates summaries, and offers suggestions for improvements based on best practices in software engineering.

## Features
- Automatically retrieves changesets from GitHub pull requests.
- Uses OpenAI's API to generate summaries and feedback on code changes.
- Posts feedback as comments on GitHub pull requests.
- Supports test mode for local testing without posting to GitHub.

## Installation

### Prerequisites
- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- GitHub access token with repository access
- OpenAI API key

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/git-code-review.git
   cd git-code-review
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your GitHub and OpenAI API keys:
     ```
     GITHUB_ACCESS_TOKEN=your_github_token
     OPENAI_API_KEY=your_openai_api_key
     ```

## Usage

### Running the Lambda Function Locally
To test the Lambda function locally, you can use the `test_main.py` script:

```bash
python git-code-review/test_main.py
```

### Deploying to AWS Lambda
1. Package the application for deployment.
2. Deploy the package to AWS Lambda using your preferred deployment method.

## Contributing
We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch to your fork.
4. Open a pull request with a detailed description of your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
For questions or support, please contact the project maintainers at [your-email@example.com].
