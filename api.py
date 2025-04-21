from flask import Flask, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore
import json
import os
import logging
from src.baxus_client import BaxusClient
from src.recommendation_engine import RecommendationEngine

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
baxus_client = BaxusClient()
recommendation_engine = RecommendationEngine()

# Load the bottle data for recommendations
bottles = []
try:
    # Use absolute path based on the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, 'data', 'whiskey_data_set.json')
    
    logger.info(f"Loading whiskey data from: {data_file}")
    with open(data_file, 'r') as f:
        bottles = json.load(f)
    
    logger.info(f"Successfully loaded {len(bottles)} whiskey bottles")
    
    # Validate data structure (basic check)
    if not isinstance(bottles, list) or len(bottles) == 0:
        logger.error("Whiskey data appears to be empty or not in expected format")
except Exception as e:
    logger.error(f"Failed to load whiskey data: {str(e)}")

@app.route('/recommendations/<username>', methods=['GET'])
def get_recommendations(username):
    """General recommendations endpoint"""
    try:
        # Get user bar data
        user_bar = baxus_client.get_user_bar(username)
        if not user_bar:
            return jsonify({"error": "Could not fetch user bar data"}), 400
        
        # Get user wishlist if available
        user_wishlist = baxus_client.get_user_wishlist(username)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            username=username,
            user_bar=user_bar,
            user_wishlist=user_wishlist,
            bottles=bottles
        )
        
        # Filter to ensure only bottles from the dataset are included
        available_rankings = {bottle.get('ranking') for bottle in bottles if 'ranking' in bottle}
        filtered_recommendations = []
        
        for rec in recommendations:
            # Check if recommendation exists in our dataset
            if rec.get('bottle_data', {}).get('ranking') in available_rankings:
                rec['suggestion_type'] = "General recommendation based on collection analysis"
                filtered_recommendations.append(rec)
        
        return jsonify(filtered_recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations/<username>/similar-price', methods=['GET'])
def get_recommendations_by_price(username):
    """Recommendations within similar price ranges"""
    try:
        # Get user bar data
        user_bar = baxus_client.get_user_bar(username)
        if not user_bar:
            return jsonify({"error": "Could not fetch user bar data"}), 400
            
        # Get price range parameters (optional)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Generate price-based recommendations
        recommendations = recommendation_engine.generate_price_based_recommendations(
            username=username,
            user_bar=user_bar,
            bottles=bottles,
            min_price=min_price,
            max_price=max_price
        )
        
        # Filter to ensure only bottles from the dataset are included
        available_rankings = {bottle.get('ranking') for bottle in bottles if 'ranking' in bottle}
        filtered_recommendations = []
        
        for rec in recommendations:
            # Check if recommendation exists in our dataset
            if rec.get('bottle_data', {}).get('ranking') in available_rankings:
                rec['suggestion_type'] = "Recommendation within similar price range"
                filtered_recommendations.append(rec)
        
        return jsonify(filtered_recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations/<username>/similar-profile', methods=['GET'])
def get_recommendations_by_profile(username):
    """Recommendations with similar profiles to existing collection"""
    try:
        # Get user bar data
        user_bar = baxus_client.get_user_bar(username)
        if not user_bar:
            return jsonify({"error": "Could not fetch user bar data"}), 400
            
        # Optional profile focus parameter
        profile_focus = request.args.get('focus', default=None)
        
        # Generate profile-based recommendations
        recommendations = recommendation_engine.generate_profile_based_recommendations(
            username=username,
            user_bar=user_bar,
            bottles=bottles,
            profile_focus=profile_focus
        )
        
        # Filter to ensure only bottles from the dataset are included
        available_rankings = {bottle.get('ranking') for bottle in bottles if 'ranking' in bottle}
        filtered_recommendations = []
        
        for rec in recommendations:
            # Check if recommendation exists in our dataset
            if rec.get('bottle_data', {}).get('ranking') in available_rankings:
                rec['suggestion_type'] = "Recommendation with similar profile to your collection"
                filtered_recommendations.append(rec)
        
        return jsonify(filtered_recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations/<username>/complementary', methods=['GET'])
def get_complementary_recommendations(username):
    """Recommendations for bottles that diversify a collection"""
    try:
        # Get user bar data
        user_bar = baxus_client.get_user_bar(username)
        if not user_bar:
            return jsonify({"error": "Could not fetch user bar data"}), 400
            
        # Generate diversifying recommendations
        recommendations = recommendation_engine.generate_complementary_recommendations(
            username=username,
            user_bar=user_bar,
            bottles=bottles
        )
        
        # Filter to ensure only bottles from the dataset are included
        available_rankings = {bottle.get('ranking') for bottle in bottles if 'ranking' in bottle}
        filtered_recommendations = []
        
        for rec in recommendations:
            # Check if recommendation exists in our dataset
            if rec.get('bottle_data', {}).get('ranking') in available_rankings:
                rec['suggestion_type'] = "Complementary addition to diversify your collection"
                filtered_recommendations.append(rec)
        
        return jsonify(filtered_recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/direct-recommendations/<username>', methods=['GET'])
def get_direct_recommendations(username):
    """Generate whisky recommendations directly without storing in a file"""
    try:
        # Get user bar data
        user_bar = baxus_client.get_user_bar(username)
        if not user_bar:
            return jsonify({"error": "Could not fetch user bar data"}), 400
        
        # Get user wishlist if available
        user_wishlist = baxus_client.get_user_wishlist(username)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            username=username,
            user_bar=user_bar,
            user_wishlist=user_wishlist,
            bottles=bottles
        )
        
        # Filter to ensure only bottles from the dataset are included
        available_rankings = {bottle.get('ranking') for bottle in bottles if 'ranking' in bottle}
        filtered_recommendations = []
        
        for rec in recommendations:
            # Check if recommendation exists in our dataset
            if rec.get('bottle_data', {}).get('ranking') in available_rankings:
                rec['suggestion_type'] = "Direct personalized recommendation based on analysis"
                filtered_recommendations.append(rec)
        
        return jsonify(filtered_recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 2005))
    app.run(host='0.0.0.0', port=port)
    