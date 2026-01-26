class EmailWriter:
    def __init__(self, llm):
        self.llm = llm

    def generate_template_email(self, name, product, description, target_audience):
        """Fallback template-based email generation"""
        subject = f"Exciting opportunity for {target_audience}s like you"
        
        body = f"""Dear {name},

I noticed your impressive work as a {target_audience}, and I thought you might be interested in {product}.

{description}

Many {target_audience}s face challenges with efficiency and workflow optimization. {product} is specifically designed to address these pain points and help professionals like you achieve more.

Would you be open to a quick conversation about how {product} could benefit your work?

Best regards,
Srinivas"""
        
        return f"Subject: {subject}\n\n{body}"

    def write_email(self, name, product, description, target_audience):
        prompt = f"""
Write a high-converting cold email to {name}.

Context:
- Product Name: {product}
- Product Description: {description}
- Target Audience: {target_audience} (The recipient fits this profile)
- Sender: Srinivas

Guidelines:
1. Start with a personalized hook related to them being a {target_audience}.
2. Introduce {product} as a solution to a specific pain point they likely face.
3. Keep it concise (under 150 words).
4. Use a professional yet conversational tone.
5. End with a soft call-to-action (e.g., "Worth a chat?").

Email Draft:
Subject: [Generate a Catchy Subject Line]

Dear {name},
[Body of the email]

Best regards,
Srinivas
"""
        try:
            return self.llm.generate(prompt)
        except Exception as e:
            # If LLM fails, use template-based generation
            print(f"LLM generation failed: {str(e)}. Using template fallback.")
            return self.generate_template_email(name, product, description, target_audience)
