import json
from typing import List, Dict, Any, Optional
from src.llm_client import LLMClient
from src.remote_llm_client import RemoteLLMClient
import config

class RecommendationEngine:
    """Engine for generating whisky recommendations"""
    
    def __init__(self):
        # Initialize LLM client based on config
        if config.LLM_PROVIDER == 'anthropic':
            self.llm_client = LLMClient(provider='anthropic')
        else:
            self.llm_client = RemoteLLMClient()
    
    def generate_recommendations(self, username: str, user_bar: Dict, 
                                user_wishlist: Optional[Dict] = None, 
                                bottles: Optional[List[Dict]] = None) -> List[Dict]:
        """Generate general recommendations based on user's collection"""
        # Process bar data
        bottles_owned = self._process_bar_data(user_bar)
        
        # Extract wishlist bottles if available
        wishlist_bottles = []
        if user_wishlist:
            wishlist_bottles = self._process_wishlist_data(user_wishlist)
        
        # Build prompt
        prompt = self._build_recommendation_prompt(bottles_owned, wishlist_bottles)
        
        # Generate recommendations using LLM
        recommendations = self._generate_llm_recommendations(prompt, bottles)
        
        return recommendations
    
    def generate_price_based_recommendations(self, username: str, user_bar: Dict,
                                           bottles: List[Dict], 
                                           min_price: Optional[float] = None,
                                           max_price: Optional[float] = None) -> List[Dict]:
        """Generate recommendations within similar price ranges"""
        bottles_owned = self._process_bar_data(user_bar)
        
        # Calculate price range if not specified
        if min_price is None or max_price is None:
            avg_price = self._calculate_average_price(bottles_owned, bottles)
            # Default to ±30% of average price if not specified
            min_price = min_price or avg_price * 0.7
            max_price = max_price or avg_price * 1.3
        
        # Build price-focused prompt
        prompt = self._build_price_recommendation_prompt(
            bottles_owned, min_price, max_price
        )
        
        # Generate recommendations
        recommendations = self._generate_llm_recommendations(prompt, bottles)
        
        return recommendations
    
    def generate_profile_based_recommendations(self, username: str, user_bar: Dict,
                                             bottles: List[Dict],
                                             profile_focus: Optional[str] = None) -> List[Dict]:
        """Generate recommendations similar to existing bottles"""
        bottles_owned = self._process_bar_data(user_bar)
        
        # Build flavor profile focused prompt
        prompt = self._build_profile_recommendation_prompt(
            bottles_owned, profile_focus
        )
        
        # Generate recommendations
        recommendations = self._generate_llm_recommendations(prompt, bottles)
        
        return recommendations
    
    def generate_complementary_recommendations(self, username: str, user_bar: Dict,
                                             bottles: List[Dict]) -> List[Dict]:
        """Generate recommendations that diversify a collection"""
        bottles_owned = self._process_bar_data(user_bar)
        
        # Build diversity-focused prompt
        prompt = self._build_complementary_recommendation_prompt(bottles_owned)
        
        # Generate recommendations
        recommendations = self._generate_llm_recommendations(prompt, bottles)
        
        return recommendations

    def _clean_markdown_code_blocks(self, text):
        """Remove markdown code block delimiters from text"""
        import re
        # Remove ```json and ``` markers
        cleaned = re.sub(r'```(?:json)?\n', '', text)
        cleaned = re.sub(r'```', '', cleaned)
        return cleaned.strip()
        def _process_bar_data(self, user_bar: Dict) -> List[Dict]:
            """Extract and process bottles from user's bar data"""
            bottles = []
            if user_bar and "bottles" in user_bar:
                bottles = user_bar["bottles"]
            return bottles
    
    def _process_wishlist_data(self, user_wishlist: Dict) -> List[Dict]:
        """Extract and process bottles from user's wishlist data"""
        bottles = []
        if user_wishlist and "bottles" in user_wishlist:
            bottles = user_wishlist["bottles"]
        return bottles
    
    def _calculate_average_price(self, bottles_owned: List[Dict], all_bottles: List[Dict]) -> float:
        """Calculate average price of bottles in user's collection"""
        total_price = 0.0
        count = 0
        
        # Get bottle IDs from user's collection
        bottle_ids = [bottle.get("id") for bottle in bottles_owned]
        
        # Find these bottles in the complete dataset to get prices
        for bottle in all_bottles:
            if bottle.get("id") in bottle_ids:
                if "fair_price" in bottle:
                    total_price += bottle["fair_price"]
                    count += 1
                elif "avg_msrp" in bottle:
                    total_price += bottle["avg_msrp"]
                    count += 1
        
        # Return average or default value if no price data
        return total_price / count if count > 0 else 50.0  # Default $50 if no data
    
    def _build_recommendation_prompt(self, bottles_owned: List[Dict], 
                                    wishlist_bottles: List[Dict]) -> str:
        """Build a general recommendation prompt based on collection"""
        prompt = f"I have {len(bottles_owned)} bottles in my whisky collection:\n"
        
        # Add bottle details to the prompt
        for bottle in bottles_owned[:20]:  # Limit to 20 bottles to keep prompt size reasonable
            prompt += f"- {bottle.get('name', 'Unknown Bottle')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        if wishlist_bottles:
            prompt += f"\nI also have {len(wishlist_bottles)} bottles in my wishlist:\n"
            for bottle in wishlist_bottles[:10]:
                prompt += f"- {bottle.get('name', 'Unknown Bottle')}\n"
        
        prompt += "\nBased on my collection, recommend 5 whisky bottles I should try next. "
        prompt += "Be very concise and brief. For each recommendation, provide only the bottle name and a one-sentence reasoning. "
        prompt += "Keep the entire response under 100 words total."
        
        return prompt
    
    def _build_price_recommendation_prompt(self, bottles_owned: List[Dict],
                                          min_price: float, max_price: float) -> str:
        """Build a prompt for price-based recommendations"""
        prompt = f"I have {len(bottles_owned)} bottles in my whisky collection. "
        prompt += f"I'm looking for recommendations in the ${min_price:.2f}-${max_price:.2f} price range.\n\n"
        
        # Add some bottle details to the prompt
        for bottle in bottles_owned[:15]:
            prompt += f"- {bottle.get('name', 'Unknown Bottle')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        prompt += f"\nBased on my collection, recommend 5 whisky bottles within the ${min_price:.2f}-${max_price:.2f} price range. "
        prompt += "For each recommendation, provide the bottle name, reasoning that includes flavor profile, "
        prompt += "and how it relates to my current collection."
        
        return prompt
    
    def _build_profile_recommendation_prompt(self, bottles_owned: List[Dict],
                                           profile_focus: Optional[str] = None) -> str:
        """Build a prompt for flavor profile recommendations"""
        prompt = f"I have {len(bottles_owned)} bottles in my whisky collection:\n"
        
        # Add bottle details to the prompt
        for bottle in bottles_owned[:15]:
            prompt += f"- {bottle.get('name', 'Unknown Bottle')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        prompt += "\nBased on my collection, recommend 5 whisky bottles with similar flavor profiles"
        
        if profile_focus:
            prompt += f" particularly focusing on {profile_focus} characteristics"
        
        prompt += ". For each recommendation, provide the bottle name, detailed flavor profile description, "
        prompt += "and how it relates to specific bottles in my current collection."
        
        return prompt
    
    def _build_complementary_recommendation_prompt(self, bottles_owned: List[Dict]) -> str:
        """Build a prompt for recommendations that diversify the collection"""
        prompt = f"I have {len(bottles_owned)} bottles in my whisky collection:\n"
        
        # Get types of spirits in the collection
        spirit_types = set()
        for bottle in bottles_owned:
            if "spirit_type" in bottle and bottle["spirit_type"]:
                spirit_types.add(bottle["spirit_type"])
        
        # Add bottle details to the prompt
        for bottle in bottles_owned[:15]:
            prompt += f"- {bottle.get('name', 'Unknown Bottle')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        prompt += "\nBased on my collection, recommend 5 whisky bottles that would diversify my collection "
        prompt += "and give me new flavor experiences different from what I already have. "
        
        if spirit_types:
            prompt += f"I currently have {', '.join(spirit_types)} in my collection. "
        
        prompt += "For each recommendation, provide the bottle name, explanation of how it differs from my current collection, "
        prompt += "and what unique characteristics it would add."
        prompt += "Be extremely concise - limit each section to 1-2 sentences maximum."
        
        return prompt
    
    def _build_analysis_prompt(self, bottles_owned: List[Dict]) -> str:
        """Build a prompt for collection analysis"""
        prompt = f"I have {len(bottles_owned)} bottles in my whisky collection:\n"
        
        # Add bottle details to the prompt
        for bottle in bottles_owned:
            prompt += f"- {bottle.get('name', 'Unknown Bottle')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        prompt += "\nPlease analyze my whisky collection and provide:\n"
        prompt += "1. An overall assessment of my whisky preferences\n"
        prompt += "2. Dominant flavor profiles I seem to prefer\n"
        prompt += "3. Any gaps or categories missing from my collection\n"
        prompt += "4. 5 specific bottle recommendations that would complement my collection\n"
        prompt += "Format your analysis as JSON with sections for 'preferences', 'flavor_profile', 'gaps', and 'recommendations'. "
        prompt += "Be extremely concise - limit each section to 1-2 sentences maximum."
        
        return prompt
    
    def _generate_llm_recommendations(self, prompt: str, all_bottles: List[Dict]) -> List[Dict]:
        """Generate recommendations using LLM and match with actual bottles"""
        # Get recommendation text from LLM
        llm_response = self.llm_client.generate_recommendation(prompt)
        
        # Clean the response of markdown code blocks
        cleaned_response = self._clean_markdown_code_blocks(llm_response)
        
        # Process LLM response into structured recommendations
        try:
            # Try to parse as JSON first
            recommendations = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # If not JSON, process as text and try to extract recommendations
            recommendations = self._extract_recommendations_from_text(llm_response)
        
        # Match recommendations with actual bottle data if available
        if all_bottles:
            self._enhance_recommendations_with_bottle_data(recommendations, all_bottles)
        
        return recommendations
    
    def _extract_recommendations_from_text(self, text: str) -> List[Dict]:
        """Extract recommendations from unstructured text response"""
        # Simple extraction logic - look for numbered items or sections
        recommendations = []
        
        # Split by numbered items like "1." or "1)"
        import re
        sections = re.split(r'\d+[\.\)]', text)
        
        # Skip first section if it's just an intro
        sections = sections[1:] if len(sections) > 1 else sections
        
        for i, section in enumerate(sections[:5]):  # Limit to 5 recommendations
            if section.strip():
                # Try to extract bottle name from the beginning of the section
                lines = section.strip().split('\n')
                name = lines[0].strip()
                
                # If the first line contains a colon, use the text before it as name
                if ':' in name:
                    name = name.split(':', 1)[0].strip()
                
                # Remove any leading/trailing quotes or special characters
                name = re.sub(r'^["\'\s-]+|["\'\s-]+$', '', name)
                
                # Rest of the text is reasoning
                reasoning = section.strip()
                if name and name in reasoning:
                    reasoning = reasoning.replace(name, '', 1).strip()
                
                recommendations.append({
                    "name": name,
                    "reasoning": reasoning,
                    "relationship": "Complementary addition to bar"  # Default relationship
                })
        
        return recommendations
    
    def _enhance_recommendations_with_bottle_data(self, recommendations: List[Dict], all_bottles: List[Dict]):
        """Add actual bottle data to recommendations by matching names"""
        for rec in recommendations:
            # Skip if already has bottle_data
            if "bottle_data" in rec:
                continue

            bottle_name = rec.get("name", "").lower()

            # Try to find matching bottle
            for bottle in all_bottles:
                if bottle.get("name", "").lower() == bottle_name:
                    rec["bottle_data"] = bottle
                    break
                
    def _process_bar_data(self, user_bar: Dict) -> List[Dict]:
        """Process user's bar data to extract bottle information"""
        bottles_owned = []
        
        # Check if bar data contains bottles
        if user_bar and "bottles" in user_bar:
            bottles_owned = user_bar["bottles"]
        
        # Add additional processing here if needed
        
        return bottles_owned

def _process_wishlist_data(self, user_wishlist: Dict) -> List[Dict]:
        """Process user's wishlist data to extract bottle information"""
        wishlist_bottles = []
        
        # Check if wishlist data contains bottles
        if user_wishlist and "bottles" in user_wishlist:
            wishlist_bottles = user_wishlist["bottles"]
        
        # Add additional processing here if needed
        
        return wishlist_bottles

def _build_recommendation_prompt(self, bottles_owned: List[Dict], wishlist_bottles: List[Dict]) -> str:
        """Build a prompt for general recommendations"""
        prompt = f"I have {len(bottles_owned)} bottles in my whisky collection:\n"
        
        # Add bottle details to the prompt
        for bottle in bottles_owned[:15]:  # Limit to first 15 to avoid overly long prompts
            prompt += f"- {bottle.get('name', 'Unknown Bottle')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        if wishlist_bottles:
            prompt += f"\nI have {len(wishlist_bottles)} bottles on my wishlist, including:\n"
            for bottle in wishlist_bottles[:5]:  # Show just a few wishlist bottles
                prompt += f"- {bottle.get('name', 'Unknown Bottle')}\n"
        
        prompt += "\nBased on my collection, recommend 5 whisky bottles that would be good additions. "
        prompt += "For each recommendation, provide the bottle name, reasoning behind the recommendation, "
        prompt += "and how it relates to my current collection."
        
        return prompt
