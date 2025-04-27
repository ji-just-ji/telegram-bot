import json
import re
import unicodedata

import numpy as np


class GameController:
    """Controls game logic for different game types"""
    
    def __init__(self, config, embedding_service, counter, logger):
        self.config = config
        self.embedding_service = embedding_service
        self.counter = counter
        self.logger = logger
        self.loser = ""
        with open("char_list.json", "r") as file:
            self.char_list = json.load(file)
        self.one_dot_list = self.char_list["one_dot_list"]
        self.two_dots_list = self.char_list["two_dots_list"]
        self.three_dots_list = self.char_list["three_dots_list"]
        self.loop_map = self.char_list["loop_map"]
        self.alias_map = self.char_list["alias_map"]
        
    async def check_trigger(self, event):
        """Game 1: Check for a specific word or sticker in the message"""
        if self.config.trigger_type == "WORD":
            return await self._check_word(event)
        elif self.config.trigger_type == "STICKER":
            return await self._check_sticker(event)
        else:
            self.logger.error("Invalid TRIGGER_TYPE specified.")
            return False
    
    async def _check_word(self, event):
        """Check if message contains the trigger word"""
        text = event.raw_text or ""
        lower_text = text.lower()
        lower_trigger = self.config.trigger_word.lower()
        escaped_trigger = re.escape(self.config.trigger_word)
        pattern = r'\b' + escaped_trigger + r'\b'
    
        match = False
    
        if self.config.match_type == "EXACT":
            match = text == self.config.trigger_word
        elif self.config.match_type == "EXACT IGNORE PUNCTUATION":
            match = bool(re.search(pattern, text))
        elif self.config.match_type == "EXACT IGNORE CASE":
            match = lower_text == lower_trigger
        elif self.config.match_type == "EXACT IGNORE CASE AND PUNCTUATION":
            match = bool(re.search(pattern, lower_text))
        elif self.config.match_type == "CONTAINS":
            match = bool(re.search(escaped_trigger, text, re.IGNORECASE))
    
        return match
    
    async def _check_sticker(self, event):
        """Check if message contains the trigger sticker"""
        if event.media and hasattr(event.media, 'document'):
            if event.media.document.id == self.config.trigger_id:
                return True
        return False
        
    async def check_target_count(self):
        """Game 2: Check if message is the nth message"""
        if self.counter.message_count == self.counter.target_count:
            return True
        return False
    
    async def check_buffer(self, event):
        """Game 3: Check if the word hasn't been said in too long"""
        if not await self.check_trigger(event):
            self.counter.last_trigger += 1
            if self.counter.last_trigger >= self.config.buffer:
                self.counter.last_trigger = 0
                return True
        else:
            self.counter.last_trigger = 0
        return False
      
    async def check_correct_answer(self, event, threshold=0.85):
        """Game 4: Check if message is a correct answer"""
        text = event.raw_text or ""
        if not text.lower().lstrip('"').rstrip('"').startswith('answer'):
            self.logger.info("Message does not start with 'answer'.")
            return False
        
        if "oiiai" not in text.lower() and self.config.game == 4:
            self.logger.info("Message doesn't contains 'oiiai'.")
            return False
        
        message_embedding = self.embedding_service.get_embedding(text)
        similarities = []
        wrong_similarities = []
        
        for ref_embedding in self.embedding_service.reference_embedding:
            similarity = np.dot(ref_embedding, message_embedding) / (
                np.linalg.norm(ref_embedding) * np.linalg.norm(message_embedding)
            )
            similarities.append(similarity)
        
        for ref_wrong_embedding in self.embedding_service.reference_wrong_embedding:
            wrong_similarity = np.dot(ref_wrong_embedding, message_embedding) / (
                np.linalg.norm(ref_wrong_embedding) * np.linalg.norm(message_embedding)
            )
            wrong_similarities.append(wrong_similarity)
        
        average_similarity = np.mean(similarities)
        average_wrong_similarity = np.mean(wrong_similarities)
        self.logger.info(f"Average similarity: {average_similarity}")
        self.logger.info(f"Average wrong similarity: {average_wrong_similarity}")
        
        close_enough = average_similarity >= threshold and average_wrong_similarity < 0.8
        self.logger.info(f"Close enough: {close_enough}")
        
        return close_enough
        
    async def check_trigger_condition(self, event):
        """Game 4: Check if message matches trigger condition"""
        self.logger.info(f"Condition: {self.config.trigger_condition}")
        
        if self.config.trigger_condition == "DOTS":
            return await self.check_dot_count(event, self.config.trigger_condition_value)
        elif self.config.trigger_condition == "SPACES":
            return await self.check_spaces(event, self.config.trigger_condition_value)
        elif self.config.trigger_condition == "LOOPS":
            return await self.check_loop_count(event, self.config.trigger_condition_value)
        elif self.config.trigger_condition == "OIIAI":
            return await self.check_oiiai(event)
        else:
            self.logger.error("Invalid TRIGGER_CONDITION specified.")
            return False
        
    async def check_dot_count(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        text.unicodedata.normalize('NFD', text)
        
        
        dot_count = sum(text.count(dot) for dot in self.one_dot_list) + \
            sum(text.count(dot) * 2 for dot in self.two_dots_list) + \
            sum(text.count(dot) * 3 for dot in self.three_dots_list)
            
        
        if dot_count == count:
            self.logger.info(f"Dot count reached: {dot_count}")
            return True

        return False
    
    async def check_spaces(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        space_count = text.count(" ")
        
        if space_count == count:
            self.logger.info(f"Space count reached: {space_count}")
            return True

        return False
    
    
    def normalize_char(self, char):
        decomposed = unicodedata.normalize('NFD', char)
        base = ''.join(c for c in decomposed if not unicodedata.combining(c))
        return self.alias_map.get(base, base)
    
    async def check_loop_count(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        text = unicodedata.normalize('NFD', text)
        loop_count = 0
        
        for char in text:
            if unicodedata.combining(char):
                continue
                
            base_char = self.normalize_char(char)
            loops = self.loop_map.get(base_char, 0)
            loop_count += loops
            
        self.logger.info(f"Loop count reached: {loop_count}")
        return loop_count == count
    

    async def check_letter_count(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        letter_count = sum(1 for char in text if char.isalpha())
        
        if letter_count == count:
            self.logger.info(f"Letter count reached: {letter_count}")
            return True

        return False
    
    async def check_digit_count(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        digit_count = sum(1 for char in text if char.isdigit())
        
        if digit_count == count:
            self.logger.info(f"Digit count reached: {digit_count}")
            return True

        return False
    
    async def check_word_count(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        word_count = len(text.split())
        
        if word_count == count:
            self.logger.info(f"Word count reached: {word_count}")
            return True

        return False
    
    async def check_alphabetical_order(self, event, count=5):
        text = event.raw_text if event.raw_text else None
        word_count = len(text.split())
        
        if word_count > count:
            words = re.sub(r'[^a-zA-Z\s]', '', text).split()
            first_letters = [word[0].lower() for word in words if word]
            if first_letters == sorted(first_letters):
                self.logger.info("First letters are in alphabetical order.")
                return True

            self.logger.info("First letters are not in alphabetical order.")
        return False
    
    
    async def check_oiiai(self, event):
        text = event.raw_text if event.raw_text else ""
        vowels = "aeiou"
        text_vowels = ''.join([char for char in text.lower() if char in vowels])
        
        if "oiiai" not in text.lower() and "oiiai" == text_vowels:
            self.logger.info("Message does not contain 'oiiai', but vowels form 'oiiai'.")
            return True

        self.logger.info("Condition not met for 'oiiai'.")
        return False