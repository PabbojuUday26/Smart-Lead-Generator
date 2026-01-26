from github.github_email_finder import main as fetch_github_emails
from core.csv_manager import read_csv
from email_engine.llm_client import LLMClient
from email_engine.email_writer import EmailWriter
from mailer.send_email import send_email
import pandas as pd

def main():
    print("=== Full Outreach Automation ===")

    # Step 1: Fetch GitHub emails → saves to data/emails.csv
    fetch_github_emails()

    # Step 2: Read saved emails
    contacts = read_csv("leads.csv")

    # Step 3: Setup LLM
    llm = LLMClient()
    writer = EmailWriter(llm)

    topic = "Python Developer Opportunity"
    sender = input("Your Gmail: ")
    app_pass = input("Your Gmail App Password: ")

    # Step 4: Email each contact
    for _, row in contacts.iterrows():
        username = row["username"]
        email = row["email"]

        print(f"\nGenerating email for {username} ({email})...")
        email_text = writer.write_email(username, topic)

        send_email(
            sender=sender,
            app_password=app_pass,
            receiver=email,
            subject=topic,
            body=email_text
        )

    print("\n🎉 ALL EMAILS SENT SUCCESSFULLY!")

if __name__ == "__main__":
    main()
