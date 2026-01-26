from huggingface_hub import InferenceClient
import logging

class LLMClient:
    def __init__(self, api_key, model_name="meta-llama/Meta-Llama-3.1-8B-Instruct"):
        self.client = InferenceClient(model=model_name, token=api_key)
        self.api_key = api_key

    def generate(self, prompt):
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages, max_tokens=300, temperature=0.7)
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            logging.error(f"HuggingFace API Error: {error_msg}")
            
            # Check if it's an authentication error
            if "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception("Invalid or expired HuggingFace API key. Please update your HUGGINGFACE_API_KEY in the .env file")
            else:
                raise Exception(f"HuggingFace API Error: {error_msg}")
