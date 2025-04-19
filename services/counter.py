import os
import random


class MessageCounter:
    """Manages message counting and persistence"""
    
    def __init__(self, min_count, max_count, logger):
        self.message_count_file = 'message_count.txt'
        self.message_count = 0
        self.target_count = random.randint(min_count, max_count)
        self.last_trigger = 0
        self.logger = logger
        
        self.load_message_count()
        
    def load_message_count(self):
        """Load message count from file"""
        if os.path.exists(self.message_count_file):
            try:
                with open(self.message_count_file, 'r') as f:
                    self.message_count = int(f.read().strip())
                    self.logger.info(f"Resumed message count from file: {self.message_count}")
            except Exception as e:
                self.logger.warning(f"Failed to read message count file: {e}")
                self.message_count = 0
    
    def save_message_count(self):
        """Save message count to file"""
        try:
            with open(self.message_count_file, 'w') as f:
                f.write(str(self.message_count))
        except Exception as e:
            self.logger.error(f"Error saving message count: {e}")
    
    def increment(self):
        """Increment message count"""
        self.message_count += 1
        return self.message_count
