import json
import config
from src.data_processor import WhiskyDataProcessor
from src.llm_client import LLMClient

class BobRecommender:
    """LLM-based whisky recommendation engine"""
    
    def __init__(self, llm_client, whisky_data, data_processor):
        self.llm = llm_client
        self.whisky_data = whisky_data
        self.data_processor = data_processor
    
    def _create_llm_prompt(self, user_profile, user_collection, potential_bottles):
        """Create prompt for the LLM"""
        # Convert user's current bottles to a simple list
        user_bottles = [
            f"{b.get('name', 'Unknown')} ({b.get('region', 'Unknown')} region, "
            f"${b.get('price', 0)}, {b.get('age_statement', 'NAS')})"
            for b in user_collection
        ]
        
        # Format potential bottles for the prompt
        potential_recommendations = []
        for i, bottle in enumerate(potential_bottles):
            potential_recommendations.append(
                f"[{i}] {bottle.get('name', 'Unknown')} - "
                f"Region: {bottle.get('region', 'Unknown')}, "
                f"Price: ${bottle.get('fair_price', 0)}, "
                f"Age: {bottle.get('age_statement', 'NAS')}, "
                f"Type: {bottle.get('type', 'Unknown')}, "
                f"ABV: {bottle.get('abv', 'Unknown')}"
            )
        
        # Create a formatted string of top regions
        regions_str = ", ".join([
            f"{region} ({count} bottles)"
            for region, count in sorted(
                user_profile['regions'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        ])
        
        # Create a formatted string of top distilleries
        distilleries_str = ", ".join([
            f"{distillery} ({count} bottles)"
            for distillery, count in sorted(
                user_profile['distilleries'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        ])
        
        # Create the prompt
        prompt = f"""
You are Bob, a whisky expert who helps users discover new bottles based on their current collection.

### USER'S WHISKY COLLECTION PROFILE:
- Top regions: {regions_str}
- Price range: ${user_profile['price_range']['min']} to ${user_profile['price_range']['max']} (avg: ${user_profile['price_range']['avg']:.2f})
- Top distilleries: {distilleries_str}
- Total bottles: {user_profile['bottle_count']}

### USER'S CURRENT BOTTLES ({len(user_bottles)}):
{chr(10).join(f"- {bottle}" for bottle in user_bottles[:10])}
{f"(... and {len(user_bottles) - 10} more bottles)" if len(user_bottles) > 10 else ""}

### POTENTIAL RECOMMENDATIONS ({len(potential_recommendations)}):
{chr(10).join(potential_recommendations)}

Based on this user's collection, recommend {config.MAX_RECOMMENDATIONS} bottles from the potential recommendations list. 
For each recommendation:
1. Reference the bottle by its number [X]
2. Explain why it matches their preferences
3. Note if it's similar to bottles they already enjoy or if it would diversify their collection

Provide your recommendations in this format:
BOTTLE [X]: <Name>
REASONING: <Your explanation for why this matches their preferences>
RELATIONSHIP TO COLLECTION: <Similar to their existing collection or complementary addition>
"""
        return prompt
    
    def recommend(self, user_collection):
        """Generate personalized recommendations using LLM"""
        # Create user profile
        user_profile = self.data_processor.create_user_profile(user_collection)
        
        # Filter potential bottles
        potential_bottles = self.data_processor.filter_potential_recommendations(
            user_collection, 
            self.whisky_data, 
            config.MAX_POTENTIAL_BOTTLES
        )
        
        # Create prompt for LLM
        prompt = self._create_llm_prompt(user_profile, user_collection, potential_bottles)
        
        # Call LLM API
        llm_response = self.llm.generate_recommendation(prompt)
        
        # Parse and format recommendations
        recommendations = self._parse_recommendations(llm_response, potential_bottles)
        return recommendations
    
    # Add these new methods to your BobRecommender class

    def recommend_by_price(self, user_bar, min_price=None, max_price=None):
        """Generate recommendations within a specific price range"""
        # Calculate default price range if not provided
        if min_price is None or max_price is None:
            avg_price = self._calculate_average_price(user_bar)
            min_price = min_price or avg_price * 0.7  # 30% below average
            max_price = max_price or avg_price * 1.3  # 30% above average
        
        # Generate custom prompt for price-based recommendations
        prompt = self._build_price_range_prompt(user_bar, min_price, max_price)
        
        # Get recommendations using the price-focused prompt
        return self._generate_recommendations(prompt, user_bar)

    def recommend_similar_profiles(self, user_bar):
        """Generate recommendations with similar flavor profiles"""
        # Generate custom prompt for similar profile recommendations
        prompt = self._build_similar_profile_prompt(user_bar)
        
        # Get recommendations using the flavor profile-focused prompt
        return self._generate_recommendations(prompt, user_bar)

    def recommend_complementary(self, user_bar):
        """Generate recommendations that would diversify a collection"""
        # Generate custom prompt for complementary recommendations
        prompt = self._build_complementary_prompt(user_bar)
        
        # Get recommendations using the diversity-focused prompt
        return self._generate_recommendations(prompt, user_bar)

    def _calculate_average_price(self, user_bar):
        """Calculate the average price of bottles in the user's bar"""
        bottles = self._extract_bottles(user_bar)
        
        # Extract bottle IDs
        bottle_ids = [bottle.get("id") for bottle in bottles if bottle.get("id")]
        
        # Find these bottles in our dataset
        total_price = 0
        count = 0
        
        for bottle in self.whisky_data:
            if bottle.get("id") in bottle_ids:
                if "fair_price" in bottle:
                    total_price += bottle["fair_price"]
                    count += 1
                elif "avg_msrp" in bottle:
                    total_price += bottle["avg_msrp"]
                    count += 1
        
        # Return average or default
        return total_price / count if count > 0 else 50.0

    def _build_price_range_prompt(self, user_bar, min_price, max_price):
        """Build a prompt for price-based recommendations"""
        bottles = self._extract_bottles(user_bar)
        
        prompt = f"I have {len(bottles)} bottles in my whisky collection. "
        prompt += f"I'm looking for recommendations in the ${min_price:.2f}-${max_price:.2f} price range.\n\n"
        
        # Add bottle details
        for bottle in bottles[:15]:
            prompt += f"- {bottle.get('name', 'Unknown')}\n"
        
        prompt += f"\nRecommend 5 whisky bottles within the ${min_price:.2f}-${max_price:.2f} price range. "
        prompt += "For each recommendation, provide the bottle name, reasoning that includes flavor profile, "
        prompt += "and how it relates to my current collection."
        
        return prompt

    def _build_similar_profile_prompt(self, user_bar):
        """Build a prompt for similar flavor profile recommendations"""
        bottles = self._extract_bottles(user_bar)
        
        prompt = f"I have {len(bottles)} bottles in my whisky collection:\n"
        
        for bottle in bottles[:15]:
            prompt += f"- {bottle.get('name', 'Unknown')}\n"
        
        prompt += "\nRecommend 5 whisky bottles with similar flavor profiles to what I already enjoy. "
        prompt += "For each recommendation, provide the bottle name, detailed flavor profile description, "
        prompt += "and how it relates to specific bottles in my current collection."
        
        return prompt

    def _build_complementary_prompt(self, user_bar):
        """Build a prompt for complementary recommendations"""
        bottles = self._extract_bottles(user_bar)
        
        # Get types of spirits in collection
        spirit_types = set()
        for bottle in bottles:
            if bottle.get("spirit_type"):
                spirit_types.add(bottle["spirit_type"])
        
        prompt = f"I have {len(bottles)} bottles in my whisky collection:\n"
        
        for bottle in bottles[:15]:
            prompt += f"- {bottle.get('name', 'Unknown')}"
            if bottle.get('spirit_type'):
                prompt += f" ({bottle.get('spirit_type')})"
            prompt += "\n"
        
        prompt += "\nRecommend 5 whisky bottles that would diversify my collection "
        prompt += "and provide new flavor experiences different from what I already have. "
        
        if spirit_types:
            prompt += f"I currently have {', '.join(spirit_types)} in my collection. "
        
        prompt += "For each recommendation, provide the bottle name, explanation of how it differs from my current collection, "
        prompt += "and what unique characteristics it would add."
        
        return prompt

    def _extract_bottles(self, user_bar):
        """Extract bottle data from user bar"""
        if not user_bar or "bottles" not in user_bar:
            return []
        return user_bar["bottles"]
    
    def _parse_recommendations(self, llm_response, potential_bottles):
        """Parse LLM response into structured recommendations"""
        recommendations = []
        current_rec = {}
        
        for line in llm_response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('BOTTLE ['):
                # Save the previous recommendation if it exists
                if current_rec and 'bottle_id' in current_rec:
                    recommendations.append(current_rec)
                current_rec = {}
                
                # Extract bottle ID from format "BOTTLE [X]: Name"
                try:
                    parts = line.split(':', 1)
                    if len(parts) >= 2:
                        id_part = parts[0].strip()
                        bottle_id = int(id_part.split('[')[1].split(']')[0])
                        bottle_name = parts[1].strip()
                        
                        # Link to the actual bottle data
                        if 0 <= bottle_id < len(potential_bottles):
                            bottle_data = potential_bottles[bottle_id]
                            current_rec['bottle_id'] = bottle_id
                            current_rec['bottle_data'] = bottle_data
                            current_rec['name'] = bottle_name
                except:
                    # If parsing fails, just continue
                    pass
                    
            elif line.startswith('REASONING:'):
                reasoning_text = line.replace('REASONING:', '').strip()
                # Remove leading colon if present
                if reasoning_text.startswith(':'):
                    reasoning_text = reasoning_text[1:].strip()
                current_rec['reasoning'] = reasoning_text
                
            elif line.startswith('RELATIONSHIP TO COLLECTION:'):
                relationship_text = line.replace('RELATIONSHIP TO COLLECTION:', '').strip()
                # Remove leading colon if present
                if relationship_text.startswith(':'):
                    relationship_text = relationship_text[1:].strip()
                current_rec['relationship'] = relationship_text        
        # Add the last recommendation if it exists
        if current_rec and 'bottle_id' in current_rec:
            recommendations.append(current_rec)
            
        return recommendations[:config.MAX_RECOMMENDATIONS]