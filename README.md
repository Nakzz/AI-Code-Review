# Git Code Review

An automated code review tool that integrates with GitHub and utilizes OpenAI's API to provide intelligent feedback on pull requests. It analyzes code changes, generates summaries, and offers suggestions for improvements based on software engineering best practices.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Roadmap](#roadmap)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
  - [Running Locally](#running-locally)
  - [Deployment and Integration](#deployment-and-integration)


## Introduction

I've recently starting programming with Aider [Aider](https://aider.chat), and I wanted to practice outside of work. 

Coincidentaly OpenAI's `o1-preview` and `o1-mini` models just released this week. So over the weekend I wrote up a simple project to review my PR's that will (mostly) be written by AI, strictly using AI. 

**Note:** At the time of development:

- Project: The `o1-preview` model does not support [structured responses](https://platform.openai.com/docs/guides/structured-outputs/introduction).
- Pair programming: Initial thoughts of using Aider and the `o1-preview` model, I prefer the faster `4o`, and often times `o1-preview` rambles in other languages(Spanish, Korean, and Chinese). I'm sure OpenAI going to resolve it soon.
 

## Features

- **Automated Code Review:** Retrieves changesets from GitHub pull requests and analyzes them using AI.
- **Intelligent Feedback:** Generates summaries and constructive feedback on code changes.
- **GitHub Integration:** Posts feedback as comments directly on GitHub pull requests.
- **Test Mode:** Allows local testing without posting to GitHub, enabling safe experimentation.

## Roadmap (or not)

- **Suggested Code Changes:** Implement functionality to suggest code changes directly from the model's feedback. [Learn More](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/incorporating-feedback-in-your-pull-request#applying-a-suggested-change)
- **Customization:** Allow users to configure feedback levels and analysis depth, or simply chat back from Github PR.
- **Model Support:** Expand to support other models (Claude, Llama). 


## Installation

### Prerequisites
- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- GitHub access token with repository access
- OpenAI API key

### Setup
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
### Running Locally

To test the Lambda function locally without deploying, use the `test_main.py` script:

```bash
python git_code_review/test_main.py
```


### Deployment and Integration
1. Package the application for deployment.
2. Deploy the package to AWS Lambda using your preferred deployment method.
3. Create an API Gateway Route and Integration to the Lambda.
4. Configure your Github projects webhook to send PR events to the endpoint. 


## License
This project is licensed under the MIT License. See the LICENSE file for more details.
