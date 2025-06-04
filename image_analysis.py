import google.generativeai as genai
import io
import requests
from PIL import Image
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

async def analyze_food_image(image_url: str) -> dict:
    """
    Analyze a food image and return calorie estimation and nutritional info
    
    Args:
        image_url: URL of the image to analyze
        
    Returns:
        dict: Contains calories, food_name, confidence, and nutritional_info
    """
    if not model:
        return {
            "error": "Image analysis is not available. Gemini API key not configured.",
            "calories": 0,
            "food_name": "Unknown",
            "confidence": 0,
            "nutritional_info": {}
        }
    
    try:
        # Download the image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open and process the image
        image = Image.open(io.BytesIO(response.content))
        
        # Create a detailed prompt for food analysis
        prompt = """
        Analyze this food image and provide a detailed nutritional breakdown. Please respond in this exact JSON format:

        {
            "food_name": "specific name of the food item(s)",
            "estimated_calories": number (total calories for the portion shown),
            "confidence": number between 0-100 (how confident you are in the identification),
            "portion_size": "description of the portion size (e.g., '1 medium apple', '200g rice')",
            "nutritional_info": {
                "protein": "amount in grams",
                "carbohydrates": "amount in grams", 
                "fat": "amount in grams",
                "fiber": "amount in grams",
                "sugar": "amount in grams"
            },
            "health_notes": "brief note about nutritional value or health benefits"
        }

        Important guidelines:
        - Be as accurate as possible with calorie estimation
        - Consider the visible portion size
        - If multiple food items, provide total calories and list main items
        - If unclear, indicate lower confidence score
        - Base estimates on standard nutritional databases
        """
          # Generate content using Gemini
        try:
            response = model.generate_content([prompt, image])
            response_text = response.text.strip()
        except Exception as gemini_error:
            error_msg = str(gemini_error)
            logger.error(f"Gemini API error: {error_msg}")
            
            # Check for specific API key errors
            if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                return {
                    "error": "❌ Invalid Gemini API key. Please update your API key in the .env file.\n\n🔑 Get a new key at: https://aistudio.google.com/app/apikey",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
            elif "PERMISSION_DENIED" in error_msg:
                return {
                    "error": "❌ API access denied. Please check your Gemini API permissions and billing settings.",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
            elif "QUOTA_EXCEEDED" in error_msg:
                return {
                    "error": "❌ API quota exceeded. Please check your usage limits or upgrade your plan.",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
            else:
                return {
                    "error": f"❌ Gemini API error: {error_msg}",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
        
        # Parse the response
        
        # Try to extract JSON from the response
        import json
        try:
            # Find JSON in the response (sometimes it's wrapped in markdown)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            result = json.loads(json_text)
            
            # Validate and format the result
            return {
                "calories": result.get("estimated_calories", 0),
                "food_name": result.get("food_name", "Unknown food"),
                "confidence": result.get("confidence", 50),
                "portion_size": result.get("portion_size", "Unknown portion"),
                "nutritional_info": result.get("nutritional_info", {}),
                "health_notes": result.get("health_notes", ""),
                "error": None
            }
            
        except json.JSONDecodeError:
            # Fallback: parse manually or return a basic response
            logger.warning(f"Could not parse JSON from Gemini response: {response_text}")
            
            # Try to extract calories manually
            import re
            calorie_match = re.search(r'(\d+)\s*calorie', response_text.lower())
            calories = int(calorie_match.group(1)) if calorie_match else 0
            
            return {
                "calories": calories,
                "food_name": "Food item (analysis incomplete)",
                "confidence": 30,
                "portion_size": "Unknown",
                "nutritional_info": {},
                "health_notes": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "error": "Could not parse detailed analysis"
            }
            
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        return {
            "error": f"Could not download image: {str(e)}",
            "calories": 0,
            "food_name": "Unknown",
            "confidence": 0,
            "nutritional_info": {}
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "calories": 0,
            "food_name": "Unknown", 
            "confidence": 0,
            "nutritional_info": {}
        }

def is_image_analysis_available() -> bool:
    """Check if image analysis is available"""
    return model is not None

async def test_gemini_api() -> dict:
    """Test if the Gemini API is working properly"""
    if not model:
        return {
            "status": "error",
            "message": "Gemini API key not configured"
        }
    
    try:
        # Test with a simple text prompt
        response = model.generate_content("Say 'API test successful' if you can read this.")
        return {
            "status": "success",
            "message": "Gemini API is working correctly",
            "response": response.text.strip()
        }
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            return {
                "status": "error",
                "message": "Invalid API key. Please update your GEMINI_API_KEY in the .env file.",
                "help_url": "https://aistudio.google.com/app/apikey"
            }
        else:
            return {
                "status": "error",
                "message": f"API error: {error_msg}"
            }

async def analyze_food_with_description(image_url: str, description: str = None) -> dict:
    """
    Analyze a food image with optional text description for enhanced accuracy
    
    Args:
        image_url: URL of the image to analyze
        description: Optional text description with measurements (e.g., "350g chicken and salad")
        
    Returns:
        dict: Contains calories, food_name, confidence, and nutritional_info with enhanced accuracy
    """
    if not model:
        return {
            "error": "Image analysis is not available. Gemini API key not configured.",
            "calories": 0,
            "food_name": "Unknown",
            "confidence": 0,
            "nutritional_info": {}
        }
    
    try:
        # Download the image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open and process the image
        image = Image.open(io.BytesIO(response.content))
        
        # Create enhanced prompt that incorporates description
        if description:
            prompt = f"""
            Analyze this food image along with the user's description: "{description}"

            Use the description to enhance your analysis accuracy, especially for:
            - Portion sizes and weights mentioned (e.g., "350g", "2 cups", "1 medium")
            - Specific food items mentioned
            - Cooking methods or preparation details

            Please respond in this exact JSON format:

            {{
                "food_name": "specific name of the food item(s) incorporating user description",
                "estimated_calories": number (total calories considering both image and description),
                "confidence": number between 0-100 (should be higher with description provided),
                "portion_size": "accurate portion size based on description and visual cues",
                "user_description_used": true,
                "description_accuracy": "how well the description matches the image (good/partial/poor)",
                "nutritional_info": {{
                    "protein": "amount in grams",
                    "carbohydrates": "amount in grams", 
                    "fat": "amount in grams",
                    "fiber": "amount in grams",
                    "sugar": "amount in grams"
                }},
                "health_notes": "brief note about nutritional value, considering specific measurements provided"
            }}

            Important guidelines:
            - Prioritize the user's measurements and descriptions for portion sizes
            - Cross-reference the description with what you see in the image
            - If description conflicts with image, note it and provide your best estimate
            - Higher confidence scores when description matches visual analysis
            - Use standard nutritional databases for accurate calculations
            """
        else:
            # Use the original prompt for image-only analysis
            prompt = """
            Analyze this food image and provide a detailed nutritional breakdown. Please respond in this exact JSON format:

            {
                "food_name": "specific name of the food item(s)",
                "estimated_calories": number (total calories for the portion shown),
                "confidence": number between 0-100 (how confident you are in the identification),
                "portion_size": "description of the portion size (e.g., '1 medium apple', '200g rice')",
                "user_description_used": false,
                "nutritional_info": {
                    "protein": "amount in grams",
                    "carbohydrates": "amount in grams", 
                    "fat": "amount in grams",
                    "fiber": "amount in grams",
                    "sugar": "amount in grams"
                },
                "health_notes": "brief note about nutritional value or health benefits"
            }

            Important guidelines:
            - Be as accurate as possible with calorie estimation
            - Consider the visible portion size
            - If multiple food items, provide total calories and list main items
            - If unclear, indicate lower confidence score
            - Base estimates on standard nutritional databases
            """

        # Generate content using Gemini
        try:
            response = model.generate_content([prompt, image])
            response_text = response.text.strip()
        except Exception as gemini_error:
            error_msg = str(gemini_error)
            logger.error(f"Gemini API error: {error_msg}")
            
            # Check for specific API key errors
            if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                return {
                    "error": "❌ Invalid Gemini API key. Please update your API key in the .env file.\n\n🔑 Get a new key at: https://aistudio.google.com/app/apikey",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
            elif "PERMISSION_DENIED" in error_msg:
                return {
                    "error": "❌ API access denied. Please check your Gemini API permissions and billing settings.",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
            elif "QUOTA_EXCEEDED" in error_msg:
                return {
                    "error": "❌ API quota exceeded. Please check your usage limits or upgrade your plan.",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
            else:
                return {
                    "error": f"❌ Gemini API error: {error_msg}",
                    "calories": 0,
                    "food_name": "Unknown",
                    "confidence": 0,
                    "nutritional_info": {}
                }
        
        # Parse the response
        import json
        try:
            # Find JSON in the response (sometimes it's wrapped in markdown)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            result = json.loads(json_text)
            
            # Validate and format the result
            return {
                "calories": result.get("estimated_calories", 0),
                "food_name": result.get("food_name", "Unknown food"),
                "confidence": result.get("confidence", 50),
                "portion_size": result.get("portion_size", "Unknown portion"),
                "nutritional_info": result.get("nutritional_info", {}),
                "health_notes": result.get("health_notes", ""),
                "user_description_used": result.get("user_description_used", False),
                "description_accuracy": result.get("description_accuracy", ""),
                "original_description": description if description else "",
                "error": None
            }
            
        except json.JSONDecodeError:
            # Fallback: parse manually or return a basic response
            logger.warning(f"Could not parse JSON from Gemini response: {response_text}")
            
            # Try to extract calories manually
            import re
            calorie_match = re.search(r'(\d+)\s*calorie', response_text.lower())
            calories = int(calorie_match.group(1)) if calorie_match else 0
            
            return {
                "calories": calories,
                "food_name": "Food item (analysis incomplete)",
                "confidence": 30,
                "portion_size": "Unknown",
                "nutritional_info": {},
                "health_notes": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "user_description_used": bool(description),
                "description_accuracy": "",
                "original_description": description if description else "",
                "error": "Could not parse detailed analysis"
            }
            
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        return {
            "error": f"Could not download image: {str(e)}",
            "calories": 0,
            "food_name": "Unknown",
            "confidence": 0,
            "nutritional_info": {}
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "calories": 0,
            "food_name": "Unknown", 
            "confidence": 0,
            "nutritional_info": {}
        }
