import os

import requests


class MpesaPayment:

    def __init__(self):

        # Safaricom app credentials used to generate access token
        self.consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        self.consumer_secret = "amFbAoUByPV2rM5A"

        # Daraja B2C credentials
        self.initiator = "testapi"
        self.security_credential = "PPMASUVMORtu7gUEIBKFL+UPQDIKW/yEJnZ0F6rsocxI2rOIj5QJOM3u5kukzdwBy9kJtrcghpa8qPT4rDI5sobdhNstp1EVabfVql5BKsp25hUACi8bSBofWjx1M3YuWRQcjjFJvRJY+a0fsWAzlSuYVCxLj3Dgy8L+xKQ9S8teuvWNz6wazrON7T/bg4oQQJFoP0R0XxeNHgiKG+qdjJTecOfBAsk/FBZnIw+HaLBE3LvrGkbjZKIs2BS2SGME1iBplFjBVR1TMtDibuc04cUCD5PkRaqkyiSIAP6R+XCej+TMedCgb7InOlsxYdaJnFjThIw0zUaQC3jiivSA5A=="
        # Daraja endpoints
        self.token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.payment_url = "https://sandbox.safaricom.co.ke/mpesa/b2b/v1/paymentrequest"

        # Public HTTPS endpoint where Safaricom sends transaction results (Generated via ngrok)
        self.callback_url = "https://f0f1-102-204-88-102.ngrok-free.app/api/cooperative/callback"

    def get_token(self):
        # Requests an OAuth2 temporary access token from Safaricom
        response = requests.get( self.token_url, auth=requests.auth.HTTPBasicAuth( self.consumer_key, self.consumer_secret))

        # Return only the token
        return response.json()["access_token"]

    def pay_farmer(self, phone, amount):
        # Get temporary token before making payment request
        token = self.get_token()

        # Data sent to Safaricom
        payload = {

            "Initiator": self.initiator,
            "SecurityCredential": self.security_credential,
            "CommandID": "BusinessPayToBulk",
            "Amount": amount,
            "PartyA": "600989",  # Cooperative Shortcode
            "PartyB": "600000",
            "SenderIdentifierType": "4",
            "RecieverIdentifierType": "4",
            "AccountReference": "MILK",
            "Requester": phone,     # Farmer phone number
            "Remarks": "Milk payment",
            "QueueTimeOutURL": self.callback_url,
            "ResultURL": self.callback_url
        }

        # Send payment request to Daraja
        response = requests.post(self.payment_url, json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":"application/json"
            }
        )


        # Give Django the Safaricom response
        return response.json()
    



# # Prediction codeimport os
# import json
# import joblib
# from groq import Groq

# class CattleAIService:
#     def __init__(self):
#         # Locate files in the same directory as this file
#         base_dir = os.path.dirname(os.path.abspath(__file__))
        
#         # Load your ML assets
#         self.model = joblib.load(os.path.join(base_dir, 'cattle_disease_model.pkl'))
#         self.model_features = joblib.load(os.path.join(base_dir, 'model_features.pkl'))
        
#         # Clean symptom features list
#         self.valid_symptoms = [
#             f for f in self.model_features 
#             if f not in ['Age', 'Temperature'] and not f.startswith('Animal_')
#         ]
        
#         # Setup Groq Client
#         self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

#     def extract_symptoms_with_groq(self, farmer_text):
#         system_prompt = f"""
#         You are a veterinary assistant. Analyze the text and extract symptoms matching exactly this list:
#         {self.valid_symptoms}
#         Respond with a JSON object: {{"symptoms": ["symptom_name"]}}
#         """
#         try:
#             completion = self.groq_client.chat.completions.create(
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": f"Farmer text: \"{farmer_text}\""}
#                 ],
#                 model="llama-3.1-8b-instant",
#                 temperature=0.0,
#                 response_format={"type": "json_object"} 
#             )
#             result_json = json.loads(completion.choices.message.content)
#             return result_json.get("symptoms", [])
#         except Exception:
#             return []

#     def get_treatment_recommendation(self, disease, animal_type):
#         system_prompt = (
#             "You are an expert livestock veterinarian. Provide clear, concise, and professional "
#             "treatment recommendations under 120 words using short bullet points. Include a vet disclaimer."
#         )
#         try:
#             completion = self.groq_client.chat.completions.create(
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": f"Treatment recommendations for a {animal_type} with {disease}."}
#                 ],
#                 model="llama-3.1-8b-instant",
#                 temperature=0.3
#             )
#             return completion.choices.message.content.strip()
#         except Exception:
#             return "Treatment recommendation temporarily unavailable. Please consult your local veterinarian immediately."

#     def predict(self, animal_type, age, temp, description):
#         # 1. AI Symptom Extraction
#         extracted_symptoms = self.extract_symptoms_with_groq(description)
        
#         # 2. Prepare ML Feature Vector Map
#         input_data = {feature: 0 for feature in self.model_features}
#         input_data['Age'] = age
#         input_data['Temperature'] = temp
        
#         # Map One-Hot encoded animal key
#         animal_key = f"Animal_{str(animal_type).strip().lower()}"
#         if animal_key in input_data:
#             input_data[animal_key] = 1
            
#         # Map extracted symptoms
#         for symptom in extracted_symptoms:
#             if symptom in input_data:
#                 input_data[symptom] = 1

#         # 3. Predict using ML Model
#         final_input_vector = [input_data[feature] for feature in self.model_features]
#         prediction = self.model.predict([final_input_vector])
#         predicted_disease = prediction[0]
        
#         # 4. Generate AI Treatment Recommendation
#         treatment_plan = self.get_treatment_recommendation(predicted_disease, animal_type)
        
#         return {
#             'status': 'success', 
#             'extracted_symptoms_by_ai': extracted_symptoms,
#             'predicted_disease': predicted_disease,
#             'treatment_recommendation': treatment_plan
#         }


