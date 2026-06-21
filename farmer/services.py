import os
import json
import joblib
import warnings
from groq import Groq
from dotenv import load_dotenv 

# Mute the strict feature-name alerts from scikit-learn to keep your terminal output clean
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

class CattleAIService:
    def __init__(self):
        """
        Constructor: Loads the ML files and initializes the Groq AI engine once when the server boots.
        """
        # Find the absolute folder directory where this file lives on your server
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Read keys inside your local .env configuration file into memory
        load_dotenv()
        
        # Load your pre-trained machine learning model from disk
        self.model = joblib.load(os.path.join(base_dir, 'cattle_disease_model.pkl'))
        
        # Load the structural feature columns list your model expects as input layout
        self.model_features = joblib.load(os.path.join(base_dir, 'model_features.pkl'))
        
        # Build a list of valid symptoms by stripping away structural elements like metadata and animal types
        self.valid_symptoms = [
            f for f in self.model_features 
            if f not in ['Age', 'Temperature'] and not f.startswith('Animal_')
        ]
        
        # Setup and authenticate the secure Groq cloud pipeline client connection
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def extract_symptoms_with_groq(self, farmer_text):
        """
        Uses Groq LLM to convert a farmer's conversational text description into clean, structured symptoms.
        """
        # Tell the LLM exactly who it is and force it to respond strictly with valid symptoms in JSON format
        system_prompt = f"""
        You are a veterinary assistant. Analyze the text and extract symptoms matching exactly this list:
        {self.valid_symptoms}
        Respond with a JSON object: {{"symptoms": ["symptom_name"]}}
        """
        try:
            # Request processing from the LLM model using structured JSON output format configurations
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Farmer text: \"{farmer_text}\""}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.0, # Forces deterministic responses (always outputs the exact same match results)
                response_format={"type": "json_object"} 
            )
            # Drill down into the response payload to isolate the clean raw text string content output
            response_text = completion.choices[0].message.content.strip()
            
            # Convert the raw text string into a native Python dictionary array structure
            result_json = json.loads(response_text)
            
            # Extract and return the symptoms array list, falling back safely to an empty array list if missing
            return result_json.get("symptoms", [])
        except Exception as e:
            # Catch infrastructure or API connection drops safely to protect execution workflows
            print(f"Groq Extraction Error: {e}") 
            return []

    def get_treatment_recommendation(self, disease, animal_type):
        """
        Queries Groq LLM to generate instant medical advice and emergency isolation instructions.
        """
        system_prompt = (
            "You are an expert livestock veterinarian. Provide clear, concise, and professional "
            "treatment recommendations under 120 words using short bullet points. Include a vet disclaimer."
        )
        try:
            # Query the model to generate natural language instructions based on the ML prediction output
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Treatment recommendations for a {animal_type} with {disease}."}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3 # Higher value allows the AI to sound more creative and natural
            )
            # Return the cleaned text answer directly back to the execution sequence
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq Treatment Error: {e}")
            return "Treatment recommendation temporarily unavailable. Please consult your local veterinarian immediately."

    def predict(self, animal_type, age, temp, description):
        """
        Main Pipeline: Combines LLM text extraction, ML numerical modeling, and text generation into one call.
        """
        # 1. Use the LLM extraction utility to filter symptoms out of the incoming text string
        extracted_symptoms = self.extract_symptoms_with_groq(description)
        
        # 2. Build a baseline dictionary mapping all training feature names to zero values
        input_data = {feature: 0 for feature in self.model_features}
        
        # Map raw numerical inputs to their specific matching feature keys
        input_data['Age'] = age
        input_data['Temperature'] = temp
        
        # Convert animal string into a one-hot column key format name string (e.g., 'Animal_cow')
        animal_key = f"Animal_{str(animal_type).strip().lower()}"
        if animal_key in input_data:
            input_data[animal_key] = 1 # Flip the indicator flag value to True
            
        # Flip indicator flag values to True for every symptom extracted by the LLM
        for symptom in extracted_symptoms:
            if symptom in input_data:
                input_data[symptom] = 1

        # 3. Flatten the dictionary into an ordered list matching the exact index setup your model expects
        final_input_vector = [input_data[feature] for feature in self.model_features]
        
        # Pass the structured matrix into the ML model and pull out the first matching text answer string 
        prediction = self.model.predict([final_input_vector])
        predicted_disease = prediction[0]
        
        # 4. Generate dynamic response bullet points for the specific disease classification result
        treatment_plan = self.get_treatment_recommendation(predicted_disease, animal_type)
        
        # Return the consolidated final pipeline payload output directly back to your DRF Response engine
        return {
            'status': 'success', 
            'extracted_symptoms_by_ai': extracted_symptoms,
            'predicted_disease': predicted_disease,
            'treatment_recommendation': treatment_plan
        }
