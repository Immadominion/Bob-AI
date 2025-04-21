import os
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()

# API settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
BAXUS_API_URL = os.getenv('BAXUS_API_URL', 'http://services.baxus.co/api')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# LLM settings
LLM_PROVIDER = 'anthropic'  # options: 'openai', 'anthropic', 'gemini'
OPENAI_MODEL = 'gpt-4'  # or 'gpt-3.5-turbo' for faster, cheaper responses
ANTHROPIC_MODEL = 'claude-3-opus-20240229'
GEMINI_MODEL = "gemini-1.5-pro-latest"  # or another valid Gemini model

# Recommendation settings
MAX_RECOMMENDATIONS = 5
MAX_POTENTIAL_BOTTLES = 100  # Maximum bottles to include in the LLM prompt

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')
HUGGINGFACE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3" 