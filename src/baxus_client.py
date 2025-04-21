import requests # type: ignore
import json
from config import BAXUS_API_URL

class BaxusClient:
    """Client for fetching user data from BAXUS API"""
    
    def __init__(self, api_url=BAXUS_API_URL):
        self.api_url = api_url
        
    def get_user_bar(self, username):
        """Get user's bar data from BAXUS API"""
        try:
            response = requests.get(
                f"{self.api_url}/bar/user/{username}",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user bar: {e}")
            return None
            
    def get_user_wishlist(self, username):
        """Get user's wishlist data from BAXUS API (if available)"""
        try:
            response = requests.get(
                f"{self.api_url}/wishlist/user/{username}",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user wishlist: {e}")
            return None
        
        