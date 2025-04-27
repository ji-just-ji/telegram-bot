import json
import os
from dotenv import load_dotenv


class Config:
    """Manages application configuration from both env vars and config file"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Load config file
        with open('config.json', 'r') as f:
            self.config = json.load(f)
            
        # Telegram credentials
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.phone = os.getenv('PHONE')
        self.openai_key = os.getenv('OPENAI_API')
        
        # Chat IDs
        self.private_id = os.getenv('PRIVATE_ID')
        self.target_chat_id = os.getenv('TARGET_CHAT_ID')
        self.my_id = os.getenv('MY_ID')
        
        # Game settings
        self.game = int(self.config.get('GAME', 0))
        self.message = self.config.get('MESSAGE', "Trigger found!")
        self.count_user = self.config.get('COUNT_USER', "FALSE").upper()
        
        # Ignored users
        self.ignored_users = self.config.get('IGNORED_USERS', "").split(",")
        
        # Game 1 or 3 config
        self.trigger_type = self.config.get('TRIGGER_TYPE')
        self.trigger_word = self.config.get('TRIGGER_WORD')
        self.trigger_id = int(self.config.get('TRIGGER_ID', 0))
        self.match_type = self.config.get('MATCH_TYPE')
        self.hints = self.config.get('HINTS')
        
        # Game 2 config
        self.min_num = int(self.config.get('MINIMUM', 0))
        self.max_num = int(self.config.get('MAXIMUM', 0))
        
        # Game 3 config
        self.buffer = int(self.config.get('BUFFER', 0))
        
        # Game 4 config
        self.trigger_condition = self.config.get('TRIGGER_CONDITION')
        self.trigger_condition_value = int(self.config.get('TRIGGER_CONDITION_VALUE', 0))
        
        # Testing mode
        self.testing = True