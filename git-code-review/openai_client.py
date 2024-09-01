import openai
import json
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def review_code_with_openai(changeset, pr_title, pr_description):
    """
    Sends the code changeset to OpenAI's API for code review and returns structured output.

    Args:
        changeset (str): The git diff of code changes.
        pr_title (str): The title of the pull request.
        pr_description (str): The description/body of the pull request.

    Returns:
        dict: A dictionary containing 'pull_request_description' and 'feedback'.
    """
    prompt = (
        "You are an experienced software engineer familiar with leading tech practices in security, observability, reliability, object-oriented design, functional programming, and performance.\n"
        "Review the following git diff, focusing only on the new code added. "
        "Provide concise feedback on logic errors or general mistakes to promote better code quality, consistent variable naming, strongly typed (when applicable), and RESTful design (when applicable). Keep those explanations brief, assuming the reader prefers short text and optimal clarity. "
        "Offer code changes if needed but avoid commenting on acceptable code. "
        "If there are no improvements to suggest, provide an encouraging message to the developer. Creatively be their coding hypeman using modern-day references and jokes!\n"
        "If the Pull Request Description is missing or unknown, summarize the changes by reviewing the code and include a 'Pull Request Description' section in your review.\n"
        "Avoid commenting about the following: Using a logging library.\n\n\n"
        f"Pull Request Title: {pr_title}\n\n"
        f"Pull Request Description:\n{pr_description}\n\n"
        f"### Code Changes Begin:\n{changeset}\n### Code Changes Ends\n\n"
        "Please provide the output in the following JSON format:\n"
        "{\n"
        '  "pull_request_description": "string",\n'
        '  "feedback": "string"\n'
        "}\n"
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
        review_json = response.choices[0].message.content.strip()
        review_data = json.loads(review_json)
        print("Structured code review from OpenAI:\n", review_data)
        return review_data
    except openai.error.OpenAIError as e:
        print(f"Failed to get a response from OpenAI: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse OpenAI response as JSON: {e}")
        return None
