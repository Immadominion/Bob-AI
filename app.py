import sys
import os
import json

from src.baxus_client import BaxusClient
from src.data_processor import WhiskyDataProcessor
# Comment out or remove this line:
from src.llm_client import LLMClient
# Add this import:
# from src.local_llm_client import LocalLLMClient
# from src.remote_llm_client import RemoteLLMClient
from src.recommender import BobRecommender
from src.utils import format_recommendation, load_sample_user_data

def main():
    # Print welcome message
    print("\n" + "="*50)
    print(" Bob - Your Personal Whisky Recommendation Agent ")
    print("="*50 + "\n")
    
    # Initialize data processor and load whisky dataset
    data_processor = WhiskyDataProcessor('data/whiskey_data_set.json')
    whisky_data = data_processor.load_dataset()
    
    if not whisky_data:
        print("Error: Could not load whisky dataset. Please check the file path.")
        return
    
    # Initialize LLM client
    llm_client = LLMClient(provider='anthropic')
    
    # Initialize Local LLM client instead of using LLMClient with Gemini
    # You can specify a different model path if needed
    # llm_client = LocalLLMClient(model_path="/Users/immadominion/phi-2.Q4_K_M.gguf")
    # llm_client = RemoteLLMClient(base_url="http://195.179.229.61:5005")
    
    # Initialize LLM client with Hugging Face Mistral-7B-Instruct model
    # Get API token from environment variable or config
    # api_token = os.environ.get("HF_API_TOKEN")
    # llm_client = RemoteLLMClient(api_token=api_token, model_id="mistralai/Mistral-7B-Instruct-v0.3")
    
    # Initialize recommender
    recommender = BobRecommender(llm_client, whisky_data, data_processor)
    
    # Check if username provided as command line argument
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Fetching bar data for user: {username}")
        
        # Initialize BAXUS client and get user data
        baxus_client = BaxusClient()
        user_bar = baxus_client.get_user_bar(username)
        
        if not user_bar:
            print(f"No data found for user {username} or connection error.")
            print("Would you like to use sample data instead? (y/n)")
            use_sample = input().lower().strip()
            if use_sample == 'y':
                user_bar = load_sample_user_data()
            else:
                return
    else:
        print("No username provided. Using sample data for testing.")
        user_bar = load_sample_user_data()
    
    # Generate recommendations
    print("\nAnalyzing collection and generating recommendations...")
    recommendations = recommender.recommend(user_bar)
    
    # Display recommendations
    print("\n" + "="*50)
    print(f" Recommendations")
    print("="*50 + "\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(format_recommendation(rec, i))
        print("-" * 40)
    
    # Save recommendations to file
    save_path = "recommendations.json"
    with open(save_path, 'w') as f:
        json.dump(recommendations, f, indent=2)
    print(f"\nRecommendations saved to {save_path}")

if __name__ == "__main__":
    main()


