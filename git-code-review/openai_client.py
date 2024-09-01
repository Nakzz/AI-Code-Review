import openai
import json
from typing import List, Optional
from pydantic import BaseModel
from config import config

client = openai.Client(api_key=config.OPENAI_API_KEY)

class PullRquestDescriptionResponse(BaseModel):
    pull_request_description: str
    
class CodeSuggestion(BaseModel):
    filename: str
    old_code: str
    new_code: str
    
class CodeSuggestions(BaseModel):
    code_suggestions: Optional[List[CodeSuggestion]] = None
    
class ReviewResponse(BaseModel):
    feedback: str
    code_suggestions: Optional[List[CodeSuggestion]] = None
    refusal: Optional[str] = None 

def get_pr_summary(changeset: str) -> Optional[PullRquestDescriptionResponse]:
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
            max_completion_tokens=500,
            response_format=PullRquestDescriptionResponse
        )
        if response.choices:
            summary_json = response.choices[0].message.parsed
            review_data = PullRquestDescriptionResponse.model_validate(summary_json)
            return review_data
        return None
    except openai.OpenAIError as e:
        print(f"Failed to get PR summary from OpenAI: {e}")
        return None

def get_feedback(changeset: str, pr_title: str, pr_description: str) -> Optional[str]:
    prompt = (
        "You are an experienced software engineer familiar with leading tech practices in security, observability, reliability, object-oriented design, functional programming, and performance.\n"
        "Review the following git diff, focusing only on the new code added. "
        "Provide concise feedback on logic errors or general mistakes to promote better code quality, consistent variable naming, strongly typed (when applicable), and RESTful design (when applicable)."
        "Keep those explanations brief, assuming the reader prefers short text and optimal clarity, a list format in markdown."
        "Offer code changes if needed but avoid commenting on acceptable code. "
        "Avoid commenting about the following: Using a logging library, Deployment Configaration changes\n\n\n"
        f"Pull Request Description:\n{pr_description}\n"
        f"### Code Changes Begin:\n{changeset}\n### Code Changes Ends\n\n"
    )
    
    try:
        response = client.chat.completions.create(
            model="o1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2500,
            # response_format={ "type": "json_object" }
        )
        try:
            review_data = response.choices[0].message.content
            # review_data = ReviewResponse.model_validate(review_json)
            print("Simple Review from OpenAI:\n", review_data)
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

def get_detailed_review(changeset: str, pr_title: str, pr_description: str) -> Optional[str]:
    prompt = (
        "You are an experienced software engineer familiar with leading tech practices in security, observability, reliability, object-oriented design, functional programming, and performance.\n"
        "Review the following git diff, focusing only on the new code added. "
        "Provide detailed feedback on logic errors or general mistakes to promote better code quality, consistent variable naming, strongly typed (when applicable), and RESTful design (when applicable)."
        "Offer as many pragmatic code changes as needed but avoid commenting on acceptable code. "
        "Avoid reccomending changes about the following: Using a logging library.\n\n\n"
        f"Pull Request Description:\n{pr_description}\n"
        f"### Code Changes Begin:\n{changeset}\n### Code Changes Ends\n\n"
        "Think about the code responding, and your final response must strictly adhere to the format as such:"
        "{\"detailed_feedback\" : str}"
        
    )
    # \"code_suggestions\":[{\"filename\" : str , \"new_code\": str,\"old_code\": str}]
    try:
        response = client.chat.completions.create(
            model="o1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=6000,
        )
        try:
            detailed_review_data = response.choices[0].message.content
            # review_data = ReviewResponse.model_validate(review_json)
            print("Detailed code review from OpenAI:\n", detailed_review_data)
            return detailed_review_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during parsing: {e}")
            return None
    except openai.OpenAIError as e:
        print(f"Failed to get a response from OpenAI: {e}")
        return None

def suggest_code_changes(feedback: str, changeset: str) -> Optional[CodeSuggestions]:
    prompt = (
        "You are an experienced software engineer familiar with leading tech practices in security, observability, reliability, object-oriented design, functional programming, and performance.\n"
        f"You are provided feedback on the following output of git diff:\n\n{feedback}\n\n"
        "Based on this feedback, suggest code changes as new_code to address the issues mentioned. the old_code should be the code you suggest changing, we will be doing a regex search to make sure it matches exactly as just the code, can be replaced via the new_code.\n "
        f"Code Changes:\n{changeset}\n\n"

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
            max_completion_tokens=4000,
            response_format=CodeSuggestions
        )
        suggestions = []
        if response.choices:
            suggestions_text = response.choices[0].message.parsed
            suggestions = CodeSuggestions.model_validate(suggestions_text)
            # suggestions = [s.strip('- ').strip() for s in suggestions if s.strip()]
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
    feedback = get_feedback(changeset, pr_title, pr_summary)
    
    detailed_review = get_detailed_review(changeset, pr_title, pr_summary)
    # review.pr_summary = pr_summary
    
    if detailed_review:
        suggestions = suggest_code_changes(detailed_review, changeset)
        
    return ReviewResponse(feedback=feedback, code_suggestions=suggestions)
