import json
from collections import Counter

class WhiskyDataProcessor:
    """Process whisky dataset and user collection data"""
    
    def __init__(self, dataset_path='data/whisky_dataset.json'):
        self.dataset_path = dataset_path
        self.bottles = None
        
    def load_dataset(self):
        """Load the whisky bottle dataset"""
        try:
            with open(self.dataset_path, 'r') as f:
                self.bottles = json.load(f)
            print(f"Loaded {len(self.bottles)} bottles from dataset")
            return self.bottles
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading whisky dataset: {e}")
            return []
            
    def create_user_profile(self, user_collection):
        """Extract key information about user's collection"""
        if not user_collection:
            return {"bottle_count": 0}
            
        # Create a summary of the user's collection
        regions = Counter()
        prices = []
        distilleries = Counter()
        types = Counter()
        ages = Counter()
        
        for bottle in user_collection:
            # Count regions
            region = bottle.get('region', 'Unknown')
            regions[region] += 1
            
            # Track prices
            if 'price' in bottle and bottle['price']:
                prices.append(bottle['price'])
                
            # Count distilleries
            distillery = bottle.get('distillery', 'Unknown')
            distilleries[distillery] += 1
            
            # Count types/styles
            bottle_type = bottle.get('type', 'Unknown')
            types[bottle_type] += 1
            
            # Count age statements
            age = bottle.get('age_statement', 'NAS')
            ages[age] += 1
        
        # Create profile summary
        profile = {
            "regions": dict(regions),
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices)/len(prices) if prices else 0
            },
            "distilleries": dict(distilleries),
            "types": dict(types),
            "ages": dict(ages),
            "bottle_count": len(user_collection)
        }
        
        return profile
        
    def filter_potential_recommendations(self, user_collection, all_bottles, max_bottles=100):
        """Filter bottles not in user's collection and select a subset for recommendation"""
        if not user_collection or not all_bottles:
            return all_bottles[:max_bottles] if all_bottles else []
            
        # Get user's existing bottle IDs
        user_bottle_ids = set(b.get('id') for b in user_collection if 'id' in b)
        
        # Filter bottles not in user's collection
        potential_bottles = [b for b in all_bottles if b.get('id') not in user_bottle_ids]
        
        # Take a reasonable number of potential bottles
        return potential_bottles[:max_bottles]