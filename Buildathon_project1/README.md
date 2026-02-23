📌 AI Lead Generator

An automated outreach system that finds potential leads, generates personalized emails using an LLM, and sends them automatically via Gmail.
This project is built for Python developers, recruiters, freelancers, and startups looking to automate outreach at scale.

🚀 Features
✅ 1. GitHub Lead Finder

Searches GitHub for developers (Python by default)

Extracts public emails from:

GitHub profiles

Commit history

Public events

Saves all leads to data/emails.csv

✅ 2. AI Email Generator (LLM Powered)

Uses TinyLlama or any HuggingFace model

Generates clean, professional, personalized emails

Uses your custom email template

Automatically inserts recipient name & topic

✅ 3. Gmail Auto-Sender

Sends personalized emails to each lead

Uses Gmail App Password (secure)

Sends one-by-one with status logs

✅ 4. Modular Architecture

Code is clean, maintainable & scalable

Separate folders for GitHub, LLM, SMTP, Core

🗂 Project Structure
lead_outreach/
│
├── data/
│   └── emails.csv
│
├── github/
│   └── github_email_finder.py
│
├── email_engine/
│   ├── llm_client.py
│   ├── email_writer.py
│   ├── templates/
│   │   └── default_template.txt
│
├── mailer/
│   └── send_email.py
│
├── core/
│   ├── csv_manager.py
│   └── settings.py
│
├── main.py
├── README.md
└── requirements.txt

⚙️ Installation
1️⃣ Clone the repository
git clone https://github.com/yourusername/ai-lead-generator.git
cd ai-lead-generator

2️⃣ Install dependencies

Using UV:

uv pip install -r requirements.txt


Using normal pip:

pip install -r requirements.txt

🔑 Setup Requirements
✔ GitHub API Token

Needed to find public emails.

Go to
https://github.com/settings/tokens

Generate Fine-grained token

Enable:

Read user data

Read public repositories

Copy the token

Paste it inside
github/github_email_finder.py:

GITHUB_TOKEN = "your_token_here"

✔ Gmail App Password (Required for sending emails)

Google blocks normal logins — so create an App Password.

How to create:

Go to https://myaccount.google.com

Go to Security

Turn ON 2-Step Verification

A new option appears: App Passwords

Generate password for:

App: Mail
Device: Windows Computer


Copy the 16-character password

Use it in main.py when prompted.

▶️ How to Run
Start the full pipeline:
python main.py

The system will:

Search GitHub for Python developers

Extract public emails

Generate personalized emails

Send them automatically via Gmail SMTP

Log progress in the terminal

📧 Email Template Used
Subject: {topic}

Dear {name},

Write 4–6 natural sentences explaining the topic clearly and professionally.
Make the email sound polite, confident, and easy to read.
Keep the tone formal but friendly.

End with a positive closing line.

Best regards,
Srinivas


You can modify this inside:

email_engine/email_writer.py

🤖 Agents Overview

The system is composed of three autonomous agents, each handling a distinct stage of the outreach pipeline:

| Agent | Module | Responsibility |
|---|---|---|
| **GitHub Lead Finder Agent** | `github/github_email_finder.py` | Searches GitHub using the Search API, iterates through user profiles, commit metadata, and public push events to extract valid public email addresses. Saves results to `data/emails.csv`. |
| **LLM Email Generator Agent** | `email_engine/llm_client.py` + `email_engine/email_writer.py` | Builds a dynamic prompt with recipient name, product details, and target audience context, then calls the `meta-llama/Meta-Llama-3.1-8B-Instruct` model via the HuggingFace Inference API (`chat_completion`) to produce a personalised cold email. Falls back to a rule-based template when the API is unavailable. |
| **Email Sender Agent** | `mailer/send_email.py` | Connects to `smtp.gmail.com` over TLS using a Gmail App Password, attaches optional PDF files and links, and delivers the generated email to each lead one by one. |

---

🧠 How It Works (Under the Hood)
🔹 GitHub Scraper:

Uses GitHub Search API

Fetches usernames by language

Extracts email via:

.email field

commit metadata

events/push history

🔹 LLM Engine:

Loads TinyLlama (or any HuggingFace model)

Builds prompt dynamically

Generates personalized email

🔹 SMTP Sender:

Connects to smtp.gmail.com

Uses TLS + App Password

Sends one email per lead