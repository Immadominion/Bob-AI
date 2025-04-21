import openai
import config

class LLMClient:
    """Interface for LLM API interactions"""
    
    def __init__(self, provider=config.LLM_PROVIDER):
        self.provider = provider
        self.anthropic_client = None
        
        if provider == 'openai':
            openai.api_key = config.OPENAI_API_KEY
        elif provider == 'anthropic':
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            except ImportError:
                print("Anthropic library not installed. Install with: pip install anthropic")
                print("Falling back to OpenAI provider.")
                self.provider = 'openai'
            except Exception as e:
                print(f"Error initializing Anthropic client: {e}")
                print("Falling back to OpenAI provider.")
                self.provider = 'openai'
        elif provider == 'gemini':
            try:
                from google.generativeai import configure, GenerativeModel
                configure(api_key=config.GEMINI_API_KEY)
                self.gemini_model = GenerativeModel(model_name=config.GEMINI_MODEL)
            except ImportError:
                print("Google Generative AI SDK not installed. Install with: pip install google-generativeai")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate_recommendation(self, prompt):
        """Generate recommendations using the configured LLM"""
        if self.provider == 'openai':
            return self._generate_with_openai(prompt)
        elif self.provider == 'anthropic':
            return self._generate_with_anthropic(prompt)
        elif self.provider == 'gemini':
            return self._generate_with_gemini(prompt)
    
    def _generate_with_openai(self, prompt):
        """Generate recommendations using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are Bob, a whisky expert who specializes in personalized recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating recommendations with OpenAI: {e}")
            return "Error generating recommendations. Please try again later."
    
    def _generate_with_anthropic(self, prompt):
        """Generate recommendations using Anthropic API"""
        try:
            system_prompt = "You are Bob, a whisky expert who specializes in personalized recommendations."
            response = self.anthropic_client.messages.create(
                model=config.ANTHROPIC_MODEL,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating recommendations with Anthropic: {e}")
            return "Error generating recommendations. Please try again later."
    
    def _generate_with_gemini(self, prompt):
        """Generate recommendations using Gemini API"""
        try:
            full_prompt = "You are Bob, a whisky expert who specializes in personalized recommendations.\n\n" + prompt
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating recommendations with Gemini: {e}")
            return "Error generating recommendations. Please try again later."
