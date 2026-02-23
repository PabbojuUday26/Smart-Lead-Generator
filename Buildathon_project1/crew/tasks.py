"""
CrewAI Task definitions for the Smart Lead Generator pipeline.

Tasks are created dynamically so callers can inject campaign-specific
parameters (query, product details, etc.) at runtime.
"""

from crewai import Agent, Task


def create_find_leads_task(agent: Agent, query: str, max_results: int) -> Task:
    """Task 1: search GitHub and collect leads with public emails."""
    return Task(
        description=(
            f"Search GitHub for users matching the query '{query}'. "
            f"Collect up to {max_results} leads that have a public email address. "
            "Use the Search GitHub Leads tool with the following JSON input: "
            f'{{"query": "{query}", "max_results": {max_results}}}. '
            "Return the result exactly as a JSON array of objects with 'username' and 'email' fields."
        ),
        expected_output=(
            "A JSON array of lead objects, each containing 'username' and 'email' keys. "
            "Example: [{\"username\": \"alice\", \"email\": \"alice@example.com\"}]"
        ),
        agent=agent,
    )


def create_write_emails_task(
    agent: Agent,
    product: str,
    description: str,
    target_audience: str,
    context_tasks: list[Task],
) -> Task:
    """Task 2: generate a personalised cold email for every lead from Task 1."""
    return Task(
        description=(
            "For each lead in the previous task's output, generate a personalised cold outreach email. "
            f"Product name: '{product}'. Product description: '{description}'. "
            f"Target audience: '{target_audience}'. "
            "Use the Write Cold Email tool for each lead, passing a JSON object with "
            "'name' (the username), 'product', 'description', and 'target_audience' keys. "
            "Return a JSON array where each object has 'email' (recipient address) and 'body' (email text)."
        ),
        expected_output=(
            "A JSON array of objects, each with 'email' (recipient address) and 'body' (full email text). "
            "Example: [{\"email\": \"alice@example.com\", \"body\": \"Dear alice, ...\"}]"
        ),
        agent=agent,
        context=context_tasks,
    )


def create_send_emails_task(
    agent: Agent,
    product: str,
    context_tasks: list[Task],
) -> Task:
    """Task 3: send each generated email to its recipient."""
    return Task(
        description=(
            "Send every email from the previous task to its recipient. "
            "Use the Send Outreach Email tool for each entry, passing a JSON object with "
            f"'receiver' (email address), 'subject' ('Opportunity regarding {product}'), "
            "and 'body' (the email text) keys. "
            "Report the success or failure of each delivery."
        ),
        expected_output=(
            "A plain-text summary listing each recipient email address "
            "and whether the email was sent successfully or failed."
        ),
        agent=agent,
        context=context_tasks,
    )
