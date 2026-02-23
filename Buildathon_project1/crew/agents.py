"""
CrewAI Agent definitions for the Smart Lead Generator pipeline.

Three agents handle distinct stages of the outreach workflow:
  1. lead_finder_agent   – locates GitHub developers and collects their emails
  2. email_writer_agent  – crafts personalised cold emails with an LLM
  3. email_sender_agent  – delivers emails via Gmail SMTP
"""

import os

from crewai import Agent, LLM
from dotenv import load_dotenv

from crew.tools import search_github_leads, write_cold_email, send_outreach_email

load_dotenv()


def _get_llm() -> LLM:
    """Return a CrewAI LLM backed by the HuggingFace Inference API.
    HuggingFace's Inference API exposes an OpenAI-compatible /v1 endpoint,
    so we use CrewAI's native OpenAI provider with a custom base_url.
    The API key is read from HUGGINGFACE_API_KEY at runtime."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    return LLM(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        provider="openai",
        base_url="https://api-inference.huggingface.co/v1",
        api_key=api_key or "placeholder",
        max_tokens=300,
    )


def create_lead_finder_agent() -> Agent:
    return Agent(
        role="GitHub Lead Finder",
        goal=(
            "Search GitHub to find software developers whose profiles match the target audience "
            "and collect their publicly available email addresses."
        ),
        backstory=(
            "You are an expert technical researcher who specialises in discovering software "
            "developers on GitHub. You use the GitHub Search API to locate user profiles that "
            "match a given audience description, then extract their public emails from profiles, "
            "commit history, and public events."
        ),
        tools=[search_github_leads],
        llm=_get_llm(),
        verbose=True,
    )


def create_email_writer_agent() -> Agent:
    return Agent(
        role="Email Copywriter",
        goal=(
            "Write highly personalised, concise cold outreach emails for each lead, "
            "introducing the product and ending with a soft call-to-action."
        ),
        backstory=(
            "You are a skilled email copywriter who crafts compelling cold emails. "
            "You tailor each email to the recipient's role and likely pain points, "
            "introduce the product as a relevant solution, and keep the message under 150 words."
        ),
        tools=[write_cold_email],
        llm=_get_llm(),
        verbose=True,
    )


def create_email_sender_agent() -> Agent:
    return Agent(
        role="Email Sender",
        goal=(
            "Deliver the generated outreach emails to each lead via Gmail SMTP "
            "and report the success or failure of every delivery."
        ),
        backstory=(
            "You are responsible for the final delivery step of the outreach campaign. "
            "You take the generated email content and reliably send it to each recipient, "
            "logging a clear success or failure message for every attempt."
        ),
        tools=[send_outreach_email],
        llm=_get_llm(),
        verbose=True,
    )
