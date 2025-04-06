import gradio as gr
import requests
import os
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class TravelPlannerPromptSystem:
    def __init__(self):
        # Hugging Face API configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

                # Use environment variable for API key or default to hardcoded token
        self.hf_api_key = os.getenv('HUGGINGFACE_API_TOKEN', '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')
        
 
        
        # Check if API key is available
        if not self.hf_api_key:
            raise ValueError("Please set the HUGGINGFACE_API_TOKEN environment variable")

        # Predefined categorizations (previous categories remain the same)
        self.dietary_preferences = [
            'No Restrictions', 
            'Vegetarian', 
            'Vegan', 
            'Kosher', 
            'Halal', 
            'Gluten-Free', 
            'Dairy-Free'
        ]
        
        self.mobility_levels = [
            'Full Mobility', 
            'Limited Mobility', 
            'Wheelchair Accessible', 
            'Requires Special Assistance'
        ]
        
        self.accommodation_types = [
            'Budget', 
            'Mid-Range', 
            'Luxury', 
            'Boutique', 
            'Family-Friendly', 
            'Business Traveler'
        ]
        
        self.interest_subcategories = {
            'History': [
                'Ancient Ruins', 
                'Museums', 
                'Historical Landmarks', 
                'Archaeological Sites'
            ],
            'Food': [
                'Street Food', 
                'Fine Dining', 
                'Local Cuisine', 
                'Cooking Classes', 
                'Food Tours'
            ],
            'Nature': [
                'Hiking', 
                'Wildlife Watching', 
                'National Parks', 
                'Beaches', 
                'Scenic Landscapes'
            ],
            'Adventure': [
                'Extreme Sports', 
                'Outdoor Activities', 
                'Water Sports', 
                'Mountain Activities'
            ],
            'Art': [
                'Art Galleries', 
                'Street Art', 
                'Cultural Performances', 
                'Local Crafts'
            ]
        }

        # Budget ranges
        self.budget_ranges = {
            'low': (0, 1000),
            'moderate': (1000, 3000),
            'high': (3000, 10000),
            'luxury': (10000, float('inf'))
        }

    def interpret_budget(self, budget_input: str) -> float:
        """
        Interpret budget input flexibly
        """
        # Remove currency symbols and convert to lowercase
        clean_input = re.sub(r'[^\w\s]', '', str(budget_input)).lower()
        
        # Check for predefined ranges
        for range_name, (min_val, max_val) in self.budget_ranges.items():
            if range_name in clean_input:
                return (min_val + max_val) / 2
        
        # Try to extract numeric value
        numbers = re.findall(r'\d+', clean_input)
        if numbers:
            return float(numbers[0])
        
        # Default fallback
        return 2000  # Moderate budget default

    def interpret_interests(self, interest_input: str) -> Dict[str, List[str]]:
        """
        Flexibly interpret user's interests
        """
        # Convert to lowercase for easier matching
        clean_input = interest_input.lower()
        
        # Mapping of common interest keywords to categories and subcategories
        interest_map = {
            'history': ('History', ['Museums', 'Historical Landmarks']),
            'culture': ('History', ['Museums', 'Cultural Performances']),
            'nature': ('Nature', ['National Parks', 'Hiking', 'Scenic Landscapes']),
            'food': ('Food', ['Local Cuisine', 'Street Food', 'Food Tours']),
            'adventure': ('Adventure', ['Extreme Sports', 'Outdoor Activities']),
            'art': ('Art', ['Art Galleries', 'Street Art']),
            'relax': ('Nature', ['Beaches', 'Scenic Landscapes']),
            'explore': ('Adventure', ['Hiking', 'Wildlife Watching'])
        }
        
        # Find matching interests
        found_interests = {}
        for keyword, (main_cat, subcats) in interest_map.items():
            if keyword in clean_input:
                found_interests.setdefault(main_cat, []).extend(subcats)
        
        # If no specific interests found, provide a balanced mix
        if not found_interests:
            found_interests = {
                'History': ['Museums'],
                'Nature': ['National Parks'],
                'Food': ['Local Cuisine']
            }
        
        return found_interests

    def validate_and_refine_preferences(self, raw_preferences: Dict) -> Dict:
        """
        Validate and refine user preferences with intelligent defaults
        """
        # Create a copy to avoid modifying the original
        preferences = raw_preferences.copy()
        
        # Validate and refine destination
        if not preferences.get('destination'):
            raise ValueError("Please specify a destination. For example: 'Tokyo, Japan' or 'European trip'")
        
        # Handle flexible budget input
        if not preferences.get('budget'):
            budget_input = preferences.get('budget_description', 'moderate budget')
            preferences['budget'] = self.interpret_budget(budget_input)
        
        # Handle flexible interests
        if not preferences.get('main_interests'):
            interest_input = preferences.get('interest_description', 'mix of culture and adventure')
            interpreted_interests = self.interpret_interests(interest_input)
            
            # Extract main interests and detailed interests
            preferences['main_interests'] = list(interpreted_interests.keys())
            preferences['detailed_interests'] = [
                subcategory 
                for subcategories in interpreted_interests.values() 
                for subcategory in subcategories
            ]
        
        # Default dates if not provided
        if not all(preferences.get(date) for date in ['start_date', 'end_date']):
            next_month = datetime.now().replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            
            preferences['start_date'] = next_month.strftime('%Y-%m-%d')
            preferences['end_date'] = (next_month + timedelta(days=6)).strftime('%Y-%m-%d')
        
        # Default preferences if not specified
        preferences.setdefault('dietary_preferences', 'No Restrictions')
        preferences.setdefault('mobility_level', 'Full Mobility')
        preferences.setdefault('accommodation_type', 'Mid-Range')
        
        return preferences

    def generate_ai_travel_prompt(self, preferences: Dict) -> str:
        """
        Generate a comprehensive AI-powered travel planning prompt
        """
        return f"""You are an expert travel planner. Create a detailed travel itinerary with the following specifications:

Destination: {preferences.get('destination', 'Not specified')}
Travel Dates: {preferences.get('start_date', 'Not specified')} to {preferences.get('end_date', 'Not specified')}
Total Budget: ${preferences.get('budget', 'Not specified')}
Main Interests: {', '.join(preferences.get('main_interests', []))}
Detailed Interests: {', '.join(preferences.get('detailed_interests', []))}
Dietary Preferences: {preferences.get('dietary_preferences', 'None')}
Mobility Level: {preferences.get('mobility_level', 'Full Mobility')}
Accommodation Type: {preferences.get('accommodation_type', 'Not specified')}

Provide a comprehensive travel plan that includes:
1. Detailed daily activities tailored to interests
2. Considerations for dietary and mobility requirements
3. Estimated costs for activities and accommodations
4. Local experiences and hidden gems
5. Practical travel tips specific to the destination

Respond with a structured, easy-to-read itinerary that maximizes the traveler's experience while respecting preferences and budget constraints.
"""

    def generate_ai_itinerary(self, preferences: Dict) -> str:
        """
        Generate AI-powered travel itinerary using Hugging Face API
        """
        try:
            # Generate initial prompt
            prompt = self.generate_ai_travel_prompt(preferences)

            # Hugging Face API request
            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1500,  # Increased to allow more detailed response
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50
                }
            }

            response = requests.post(
                self.hf_api_url, 
                headers=headers, 
                json=payload
            )

            # Check response
            if response.status_code == 200:
                # Extract generated text
                generated_text = response.json()[0]['generated_text']
                
                # Remove the original prompt from the generated text
                itinerary = generated_text.replace(prompt, '').strip()
                
                return itinerary
            else:
                return f"Error generating itinerary. Status code: {response.status_code}. Response: {response.text}"

        except Exception as e:
            return f"Error generating itinerary: {str(e)}"

def create_detailed_input_interface():
    """
    Create a Gradio interface for detailed travel preference collection
    """
    planner = TravelPlannerPromptSystem()

    with gr.Blocks() as demo:
        gr.Markdown("# 🌍 AI-Powered Travel Planner")
        
        with gr.Tabs():
            with gr.Tab("Detailed Input"):
                # Initial Travel Details
                with gr.Group():
                    gr.Markdown("### Initial Travel Details")
                    destination = gr.Textbox(label="Destination")
                    start_date = gr.Textbox(label="Start Date (YYYY-MM-DD)")
                    end_date = gr.Textbox(label="End Date (YYYY-MM-DD)")
                    budget = gr.Number(label="Total Budget (USD)")
                
                # Interests and Detailed Preferences
                with gr.Group():
                    gr.Markdown("### Interests and Preferences")
                    main_interests = gr.Dropdown(
                        label="Main Interests", 
                        multiselect=True,
                        choices=list(planner.interest_subcategories.keys())
                    )
                    
                    detailed_interests = gr.Dropdown(
                        label="Specific Interest Details",
                        multiselect=True,
                        choices=[]
                    )
                
                # Dynamic interest subcategory selection
                def update_detailed_interests(main_interests):
                    detailed_choices = []
                    for interest in main_interests:
                        detailed_choices.extend(planner.interest_subcategories.get(interest, []))
                    return gr.Dropdown(choices=detailed_choices)
                
                main_interests.change(
                    fn=update_detailed_interests, 
                    inputs=main_interests, 
                    outputs=detailed_interests
                )
                
                # Additional Preferences
                with gr.Group():
                    gr.Markdown("### Additional Details")
                    dietary_pref = gr.Dropdown(
                        label="Dietary Preferences", 
                        choices=planner.dietary_preferences
                    )
                    
                    mobility_level = gr.Dropdown(
                        label="Mobility Level", 
                        choices=planner.mobility_levels
                    )
                    
                    accommodation_type = gr.Dropdown(
                        label="Accommodation Preference", 
                        choices=planner.accommodation_types
                    )
                
                # Output and Generation
                output = gr.Textbox(label="AI-Generated Travel Itinerary", lines=20)
                generate_btn = gr.Button("Generate AI Travel Plan")
            
            with gr.Tab("Flexible Input"):
                gr.Markdown("### Flexible Travel Planning")
                flexible_input = gr.Textbox(
                    label="Describe Your Dream Trip", 
                    placeholder="E.g., 'I want to visit Europe with a moderate budget, interested in history and food'"
                )
                
                flexible_destination = gr.Textbox(
                    label="Destination (if not clear from description)", 
                    placeholder="Optional: Specify exact destination"
                )
                
                flexible_dates = gr.Textbox(
                    label="Preferred Travel Dates", 
                    placeholder="Optional: E.g., 'next summer' or specific dates"
                )
                
                flexible_output = gr.Textbox(
                    label="AI-Generated Travel Itinerary", 
                    lines=20
                )
                
                generate_flexible_btn = gr.Button("Generate Flexible Travel Plan")
        
        def generate_travel_plan(
            dest, start, end, budget, main_interests, 
            detailed_interests, diet, mobility, accom
        ):
            # Prepare preferences dictionary
            preferences = {
                'destination': dest,
                'start_date': start,
                'end_date': end,
                'budget': budget,
                'main_interests': main_interests,
                'detailed_interests': detailed_interests,
                'dietary_preferences': diet,
                'mobility_level': mobility,
                'accommodation_type': accom
            }
            
            # Generate AI itinerary
            return planner.generate_ai_itinerary(preferences)
        
        generate_btn.click(
            fn=generate_travel_plan,
            inputs=[
                destination, start_date, end_date, budget,
                main_interests, detailed_interests, 
                dietary_pref, mobility_level, accommodation_type
            ],
            outputs=output
        )
        
        def generate_flexible_travel_plan(description, destination, dates):
            try:
                # Prepare preferences dictionary with flexible inputs
                preferences = {
                    'interest_description': description,
                    'destination': destination,
                }
                
                # Add date information if provided
                if dates:
                    # Simple date parsing logic
                    if 'next' in dates.lower() or 'summer' in dates.lower():
                        next_summer = datetime.now().replace(month=7, day=1)
                        preferences['start_date'] = next_summer.strftime('%Y-%m-%d')
                        preferences['end_date'] = (next_summer + timedelta(days=10)).strftime('%Y-%m-%d')
                    else:
                        # If specific dates are provided, try to parse
                        try:
                            from dateutil.parser import parse
                            parsed_dates = parse(dates, fuzzy=True)
                            preferences['start_date'] = parsed_dates.strftime('%Y-%m-%d')
                            preferences['end_date'] = (parsed_dates + timedelta(days=7)).strftime('%Y-%m-%d')
                        except:
                            # Fallback to default dates
                            pass
                
                # Validate and refine preferences
                refined_preferences = planner.validate_and_refine_preferences(preferences)
                
                # Generate AI itinerary
                itinerary = planner.generate_ai_itinerary(refined_preferences)
                
                return itinerary
            
            except ValueError as ve:
                return f"Input Clarification Needed: {str(ve)}"
            except Exception as e:
                return f"Error generating travel plan: {str(e)}"
        
        generate_flexible_btn.click(
            fn=generate_flexible_travel_plan,
            inputs=[flexible_input, flexible_destination, flexible_dates],
            outputs=flexible_output
        )

    return demo

# Launch the interface
if __name__ == "__main__":
    app = create_detailed_input_interface()
    app.launch()
