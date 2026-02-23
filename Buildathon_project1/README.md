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

✅ 5. CrewAI Agent Framework

The three stages above are wired together as a CrewAI Crew:

Three specialised agents (GitHub Lead Finder, Email Copywriter, Email Sender) each own a dedicated Task and a tool.

The Crew runs them in sequence — the output of each task is passed as context to the next.

Orchestration lives in the crew/ package; the underlying GitHub, LLM, and SMTP modules remain unchanged.

🗂 Project Structure
lead_outreach/
│
├── data/
│   └── emails.csv
│
├── crew/                        ← CrewAI layer (new)
│   ├── __init__.py
│   ├── tools.py                 ← @tool wrappers for each agent
│   ├── agents.py                ← Agent definitions
│   ├── tasks.py                 ← Task definitions
│   └── crew.py                  ← build_outreach_crew() factory
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
✔ Environment Variables (.env file)

Create a .env file in the project root with the following keys:

GITHUB_TOKEN=your_github_token
HUGGINGFACE_API_KEY=your_hf_api_key
SENDER_EMAIL=your_gmail@gmail.com
SENDER_APP_PASSWORD=your_16_char_app_password

✔ GitHub API Token

Needed to find public emails.

Go to
https://github.com/settings/tokens

Generate Fine-grained token

Enable:

Read user data

Read public repositories

Copy the token and set it as GITHUB_TOKEN in .env.

✔ HuggingFace API Key

Required for the LLM Email Generator agent.

Go to https://huggingface.co/settings/tokens

Generate a token with "Read" access.

Set it as HUGGINGFACE_API_KEY in .env.

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

Set SENDER_EMAIL and SENDER_APP_PASSWORD in .env.

▶️ How to Run
Start the full CrewAI pipeline:
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

🤖 Agents Overview (CrewAI)

The system is now built on the **CrewAI** framework. Three specialised agents are
orchestrated in a sequential `Crew`, where the output of each task feeds the next.

| Agent | CrewAI Role | Tool | Underlying Module |
|---|---|---|---|
| **GitHub Lead Finder** | `GitHub Lead Finder` | `Search GitHub Leads` | `github/github_email_finder.py` |
| **Email Copywriter** | `Email Copywriter` | `Write Cold Email` | `email_engine/llm_client.py` + `email_engine/email_writer.py` |
| **Email Sender** | `Email Sender` | `Send Outreach Email` | `mailer/send_email.py` |

The CrewAI layer lives in the `crew/` package:

- `crew/tools.py`  — `@tool`-decorated wrappers that the agents call
- `crew/agents.py` — Agent definitions (role, goal, backstory, tool, LLM)
- `crew/tasks.py`  — Task definitions with expected outputs and context links
- `crew/crew.py`   — `build_outreach_crew()` factory that wires everything into a `Crew`

All three agents share a single LLM: `meta-llama/Meta-Llama-3.1-8B-Instruct` via
HuggingFace's OpenAI-compatible Inference API (no LiteLLM required).

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