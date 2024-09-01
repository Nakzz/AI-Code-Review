import openai
import json
from pydantic import BaseModel
from config import config

client = openai.Client(api_key=config.OPENAI_API_KEY)

class ReviewResponse(BaseModel):
    pull_request_description: str
    feedback: str
    refusal: str = None 

def review_code_with_openai(changeset, pr_title, pr_description):
    """
    Sends the code changeset to OpenAI's API for code review and returns structured output.

    Args:
        changeset (str): The git diff of code changes.
        pr_title (str): The title of the pull request.
        pr_description (str): The description/body of the pull request.

    Returns:
        ReviewResponse: A structured response containing the pull request description and feedback.
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

    )
    
    try:
        response = client.beta.chat.completions.parse(
            # model="o1-mini", # TODO:(aj) doesn't support json parsing yet... maybe use this model for highlevel, and gpt40 for code changes
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2000,
            response_format=ReviewResponse
        )
        try:
            review_json = response.choices[0].message.parsed
            review_data = ReviewResponse.model_validate(review_json)
            print("Structured code review from OpenAI:\n", review_data)
            return review_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during parsing: {e}")
            return None
    except openai.OpenAIError as e:
        print(f"Failed to get a response from OpenAI: {e}")
        return None

#         "Please provide the output in the following JSON format:\n"
        # "{\n"
        # '  "pull_request_description": "string",\n'
        # '  "feedback": "string"\n'
        # "}\n"