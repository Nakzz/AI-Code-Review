import openai
import json
from typing import List, Optional
from pydantic import BaseModel
from config import config

client = openai.Client(api_key=config.OPENAI_API_KEY)

class ReviewResponse(BaseModel):
    pr_summary: Optional[str] = None
    pull_request_description: str
    feedback: str
    code_suggestions: Optional[List[str]] = None
    refusal: Optional[str] = None 

def get_pr_summary(changeset: str) -> Optional[str]:
    prompt = (
        "Analyze the following git diff and provide a concise summary of the Pull Request.\n\n"
        f"### Code Changes Begin:\n{changeset}\n### Code Changes Ends\n\n"
        "The summary should briefly describe the purpose and scope of the changes."
    )
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=500
        )
        if response.choices:
            summary = response.choices[0].message.content.strip()
            print("PR Summary from OpenAI:\n", summary)
            return summary
        return None
    except openai.OpenAIError as e:
        print(f"Failed to get PR summary from OpenAI: {e}")
        return None

def get_review(changeset: str, pr_title: str, pr_description: str) -> Optional[ReviewResponse]:
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

def suggest_code_changes(feedback: str, changeset: str) -> Optional[List[str]]:
    prompt = (
        f"You have provided feedback on the following code changes:\n\n{feedback}\n\n"
        "Based on this feedback, suggest code changes to address the issues mentioned. "
        "Provide each suggestion as a separate, concise and actionable item. "
        "If multiple changes are recommended, list them sequentially."
    )
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=1500
        )
        suggestions = []
        if response.choices:
            suggestions_text = response.choices[0].message.content.strip()
            suggestions = suggestions_text.split('\n')  # Assuming suggestions are line-separated
            suggestions = [s.strip('- ').strip() for s in suggestions if s.strip()]
            print("Code suggestions from OpenAI:\n", suggestions)
        return suggestions
    except openai.OpenAIError as e:
        print(f"Failed to get code suggestions from OpenAI: {e}")
        return None

def review_code_with_openai(changeset: str, pr_title: str, pr_description: str) -> Optional[ReviewResponse]:
    """
    Orchestrates the code review and suggestion process by making multiple OpenAI API calls.

    Steps:
        1. Generate a summary of the Pull Request based on the changeset.
        2. Review the code changes.
        3. Suggest code changes based on the review feedback.

    Args:
        changeset (str): The git diff of code changes.
        pr_title (str): The title of the pull request.
        pr_description (str): The description/body of the pull request.

    Returns:
        ReviewResponse: A structured response containing the PR summary, pull request description, feedback, and code suggestions.
    """
    pr_summary = get_pr_summary(changeset)
    review = get_review(changeset, pr_title, pr_description)
    if review is None:
        return None
    
    review.pr_summary = pr_summary
    
    if review.feedback:
        suggestions = suggest_code_changes(review.feedback, changeset)
        review.code_suggestions = suggestions
    return review
