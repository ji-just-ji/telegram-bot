import numpy as np
from openai import OpenAI
import json


class EmbeddingService:
    """Handles text embeddings using OpenAI"""
    
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
        
        # Pre-calculate embeddings if needed
        self.reference_embedding = []
        self.reference_wrong_embedding = []
    
    def get_embedding(self, text):
        """Generate embedding for a text string"""
        response = self.client.embeddings.create(input=[text], model="text-embedding-ada-002")
        return np.array(response.data[0].embedding)
        
    def initialize_embeddings(self, game, trigger_condition):
        """Pre-calculate embeddings for reference texts if using Game 4"""
        if game != 4:
            return
            
        print("Initializing embeddings for Game 4...")
        
        # Load references from references.json
        with open('references.json', 'r') as file:
            references_data = json.load(file)
        
        # Get the array corresponding to config.trigger_condition
        correct_reference = references_data.get(trigger_condition, [])
        combined_references = []
        for key, value in references_data.items():
            if key != trigger_condition:
                combined_references.extend(value)
        
        
        for ref in correct_reference:
            print(f"Reference: {ref}")
            response = self.client.embeddings.create(input=[ref], model="text-embedding-ada-002")
            self.reference_embedding.append(np.array(response.data[0].embedding))
    
        for w in combined_references:
            print(f"Wrong example: {w}")
            response = self.client.embeddings.create(input=[w], model="text-embedding-ada-002")
            self.reference_wrong_embedding.append(np.array(response.data[0].embedding))

