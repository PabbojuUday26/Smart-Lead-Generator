import os

from dotenv import load_dotenv

from crew.crew import build_outreach_crew

load_dotenv()


def main():
    print("=== Smart Lead Generator — CrewAI Pipeline ===\n")

    query = input("GitHub search query (e.g. 'Python Developer'): ").strip() or "Python Developer"
    max_results = int(input("Max leads to find (default 5): ").strip() or 5)
    product = input("Product name: ").strip()
    description = input("Product description: ").strip()
    target_audience = input("Target audience (leave blank to use search query): ").strip() or query

    if not os.getenv("SENDER_EMAIL"):
        val = input("Your Gmail address (or set SENDER_EMAIL in .env): ").strip()
        if not val:
            raise SystemExit("Error: SENDER_EMAIL is required. Set it in your .env file.")
        os.environ["SENDER_EMAIL"] = val
    if not os.getenv("SENDER_APP_PASSWORD"):
        val = input("Your Gmail App Password (or set SENDER_APP_PASSWORD in .env): ").strip()
        if not val:
            raise SystemExit("Error: SENDER_APP_PASSWORD is required. Set it in your .env file.")
        os.environ["SENDER_APP_PASSWORD"] = val

    crew = build_outreach_crew(
        query=query,
        max_results=max_results,
        product=product,
        description=description,
        target_audience=target_audience,
    )

    result = crew.kickoff()
    print("\n🎉 Campaign complete!")
    print(result)


if __name__ == "__main__":
    main()
