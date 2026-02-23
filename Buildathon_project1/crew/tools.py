"""
CrewAI custom tools that wrap the existing GitHub, LLM, and email modules.
Each tool accepts a JSON-encoded string so CrewAI agents can call them naturally.
"""

import json
import os
import sys

from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Ensure the project root is on sys.path so existing modules are importable
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


@tool("Search GitHub Leads")
def search_github_leads(query_and_count: str) -> str:
    """Search GitHub for user profiles matching the given query and return their public emails.
    Input must be a JSON string with 'query' (str) and 'max_results' (int) keys.
    Example: '{"query": "Python Developer", "max_results": 5}'
    Returns a JSON array of objects with 'username' and 'email' fields."""
    from github.github_email_finder import search_users, get_public_email

    try:
        params = json.loads(query_and_count)
        query = params.get("query", "python")
        max_results = int(params.get("max_results", 10))
    except (json.JSONDecodeError, KeyError, ValueError):
        query = query_and_count
        max_results = 10

    users = search_users(query=query, max_results=max_results)
    leads = []
    for user in users:
        username = user["login"]
        email = get_public_email(username)
        if email:
            leads.append({"username": username, "email": email})

    return json.dumps(leads)


@tool("Write Cold Email")
def write_cold_email(email_params: str) -> str:
    """Generate a personalised cold outreach email using the configured LLM.
    Input must be a JSON string with keys: 'name', 'product', 'description', 'target_audience'.
    Example: '{"name": "alice", "product": "MyTool", "description": "An AI assistant", "target_audience": "Python Developer"}'
    Returns the full email text (subject + body)."""
    from email_engine.llm_client import LLMClient
    from email_engine.email_writer import EmailWriter

    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return "Error: HUGGINGFACE_API_KEY is not set in the environment."

    try:
        params = json.loads(email_params)
    except json.JSONDecodeError:
        return "Error: Input is not valid JSON. Expected keys: name, product, description, target_audience."

    llm = LLMClient(api_key=api_key)
    writer = EmailWriter(llm)
    return writer.write_email(
        name=params.get("name", "Developer"),
        product=params.get("product", ""),
        description=params.get("description", ""),
        target_audience=params.get("target_audience", ""),
    )


@tool("Send Outreach Email")
def send_outreach_email(email_details: str) -> str:
    """Send an outreach email to a lead via Gmail SMTP.
    Input must be a JSON string with keys: 'receiver', 'subject', 'body'.
    Sender credentials are read from the SENDER_EMAIL and SENDER_APP_PASSWORD environment variables.
    Example: '{"receiver": "bob@example.com", "subject": "Hello", "body": "Hi Bob, ..."}'
    Returns a status message indicating success or failure."""
    from mailer.send_email import send_email

    sender = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("SENDER_APP_PASSWORD")

    if not sender or not app_password:
        return "Error: SENDER_EMAIL or SENDER_APP_PASSWORD is not set in the environment."

    try:
        params = json.loads(email_details)
    except json.JSONDecodeError:
        return "Error: Input is not valid JSON. Expected keys: receiver, subject, body."

    try:
        send_email(
            sender=sender,
            app_password=app_password,
            receiver=params["receiver"],
            subject=params["subject"],
            body=params["body"],
        )
        return f"Email sent successfully to {params['receiver']}."
    except KeyError as exc:
        return f"Error: Missing required field {exc} in email_details JSON."
    except Exception as exc:
        return f"Failed to send email to {params.get('receiver', 'unknown')}: {exc}"
