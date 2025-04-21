import os
from huggingface_hub import InferenceClient # type: ignore

class RemoteLLMClient:
    """Interface to Hugging Face's inference API for Mistral-7B-Instruct-v0.3"""
    
    def __init__(self, api_token=None, model_id="mistralai/Mistral-7B-Instruct-v0.3"):
        self.api_token = api_token or os.environ.get("HUGGINGFACE_API_KEY")
        self.model_id = model_id
        
        if not self.api_token:
            print("Warning: No Hugging Face API token provided. Set HF_API_TOKEN environment variable or pass as parameter.")
        
        self.client = InferenceClient(token=self.api_token)
    
    def generate_recommendation(self, prompt):
        try:
            # Format prompt for Mistral-7B-Instruct-v0.3
            formatted_prompt = self._format_prompt(prompt)
            
            # Call Hugging Face Inference API
            response = self.client.text_generation(
                formatted_prompt,
                model=self.model_id,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                return_full_text=False
            )
            
            return response
            
        except Exception as e:
            print(f"Exception contacting Hugging Face API: {e}")
            return "Hugging Face API connection failed."
    
    def _format_prompt(self, prompt):
        """Format prompt for Mistral-7B-Instruct-v0.3"""
        # Mistral format: <s>[INST] {prompt} [/INST]
        formatted_prompt = f"<s>[INST] You are Bob, a whisky expert who specializes in personalized recommendations.\n\n{prompt} [/INST]"
        return formatted_prompt