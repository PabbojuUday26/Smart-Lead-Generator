"""
Crew orchestration for the Smart Lead Generator pipeline.

build_outreach_crew() returns a ready-to-run CrewAI Crew that executes
the three-stage outreach pipeline in sequence:
  1. Find GitHub leads
  2. Write personalised emails
  3. Send the emails
"""

from crewai import Crew, Process

from crew.agents import (
    create_lead_finder_agent,
    create_email_writer_agent,
    create_email_sender_agent,
)
from crew.tasks import (
    create_find_leads_task,
    create_write_emails_task,
    create_send_emails_task,
)


def build_outreach_crew(
    query: str,
    max_results: int,
    product: str,
    description: str,
    target_audience: str,
) -> Crew:
    """
    Assemble and return a CrewAI Crew for the full lead-outreach pipeline.

    Args:
        query:           GitHub search query string (e.g. "Python Developer").
        max_results:     Maximum number of leads to collect.
        product:         Name of the product being promoted.
        description:     Short description of the product.
        target_audience: Audience label used to personalise emails.

    Returns:
        A configured Crew ready to be started with crew.kickoff().
    """
    lead_finder = create_lead_finder_agent()
    email_writer = create_email_writer_agent()
    email_sender = create_email_sender_agent()

    find_leads = create_find_leads_task(lead_finder, query, max_results)
    write_emails = create_write_emails_task(
        email_writer, product, description, target_audience, [find_leads]
    )
    send_emails = create_send_emails_task(email_sender, product, [write_emails])

    return Crew(
        agents=[lead_finder, email_writer, email_sender],
        tasks=[find_leads, write_emails, send_emails],
        process=Process.sequential,
        verbose=True,
    )
