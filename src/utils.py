def format_recommendation(rec, index=None):
    """Format a recommendation for display"""
    bottle = rec.get('bottle_data', {})
    
    # Format index if provided
    idx = f"{index}. " if index is not None else ""
    
    # Build the formatted recommendation
    output = [
        f"{idx}{rec.get('name', bottle.get('name', 'Unknown Whisky'))}",
        f"Region: {bottle.get('region', 'Unknown')}",
        f"Price: ${bottle.get('fair_price', 0)}",
        f"Age: {bottle.get('age_statement', 'NAS')}",
        f"Why this bottle: {rec.get('reasoning', 'N/A')}",
        f"Relationship to your collection: {rec.get('relationship', 'N/A')}"
    ]
    
    return "\n".join(output)

def load_sample_user_data(file_path='data/sample_user_bar.json'):
    """Load sample user data for testing"""
    import json
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return []