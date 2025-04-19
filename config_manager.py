#!/usr/bin/env python3
"""
Configuration Manager for Telegram Bot
--------------------------------------
Utility to either load an existing config.json or create a new one through interactive prompts.
"""

import json
import os
import sys
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration for the Telegram bot"""
    
    def __init__(self):
        self.config_file = 'config.json'
        self.config: Dict[str, Any] = {}
        self.default_config = {
            "GAME": 1,
            "MESSAGE": "Trigger found!",
            "COUNT_USER": "FALSE",
            "TRIGGER_TYPE": "WORD",
            "TRIGGER_WORD": "",
            "TRIGGER_ID": 0,
            "MATCH_TYPE": "EXACT",
            "HINTS": {},
            "MINIMUM": 100,
            "MAXIMUM": 500,
            "BUFFER": 10,
            "TRIGGER_CONDITION": "DOTS",
            "TRIGGER_CONDITION_VALUE": 1
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error: {self.config_file} is not a valid JSON file.")
                return {}
        return {}
    
    def save_config(self) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"Configuration saved to {self.config_file}")
    
    def get_input(self, prompt: str, default: Any = None) -> str:
        """Get input from user with default value"""
        default_display = f" [{default}]" if default is not None else ""
        user_input = input(f"{prompt}{default_display}: ").strip()
        return user_input if user_input else str(default) if default is not None else ""
    
    def get_int_input(self, prompt: str, default: Optional[int] = None) -> int:
        """Get integer input from user with default value"""
        while True:
            try:
                user_input = self.get_input(prompt, default)
                return int(user_input)
            except ValueError:
                print("Please enter a valid integer.")
    
    def configure_game_1(self) -> None:
        """Configure settings for Game 1 (trigger word/sticker)"""
        print("\n=== Game 1 Configuration (Trigger Word/Sticker) ===")
        
        self.config["TRIGGER_TYPE"] = self.get_input(
            "Trigger type (WORD/STICKER)", 
            self.config.get("TRIGGER_TYPE", self.default_config["TRIGGER_TYPE"])
        ).upper()
        
        if self.config["TRIGGER_TYPE"] == "WORD":
            self.config["TRIGGER_WORD"] = self.get_input(
                "Trigger word", 
                self.config.get("TRIGGER_WORD", self.default_config["TRIGGER_WORD"])
            )
            
            match_types = ["EXACT", "EXACT IGNORE PUNCTUATION", "EXACT IGNORE CASE", 
                          "EXACT IGNORE CASE AND PUNCTUATION", "CONTAINS"]
            print("\nMatch Types:")
            for i, match_type in enumerate(match_types, 1):
                print(f"{i}. {match_type}")
                
            while True:
                try:
                    choice = self.get_int_input(
                        "Choose match type (1-5)", 
                        match_types.index(self.config.get("MATCH_TYPE", self.default_config["MATCH_TYPE"])) + 1
                    )
                    if 1 <= choice <= 5:
                        self.config["MATCH_TYPE"] = match_types[choice - 1]
                        break
                    else:
                        print("Please enter a number between 1 and 5.")
                except ValueError:
                    print("Please enter a valid number.")
                    
        elif self.config["TRIGGER_TYPE"] == "STICKER":
            self.config["TRIGGER_ID"] = self.get_int_input(
                "Sticker ID", 
                self.config.get("TRIGGER_ID", self.default_config["TRIGGER_ID"])
            )
        else:
            print("Invalid trigger type. Using default: WORD")
            self.config["TRIGGER_TYPE"] = "WORD"
            self.config["MATCH_TYPE"] = "CONTAINS"
            self.config["TRIGGER_WORD"] = "Chicken Jocky"
    
    def configure_game_2(self) -> None:
        """Configure settings for Game 2 (target message count)"""
        print("\n=== Game 2 Configuration (Target Message Count) ===")
        
        self.config["MINIMUM"] = self.get_int_input(
            "Minimum message count", 
            self.config.get("MINIMUM", self.default_config["MINIMUM"])
        )
        
        self.config["MAXIMUM"] = self.get_int_input(
            "Maximum message count", 
            self.config.get("MAXIMUM", self.default_config["MAXIMUM"])
        )
        
        # Ensure minimum <= maximum
        if self.config["MINIMUM"] > self.config["MAXIMUM"]:
            print("Warning: Minimum count is greater than maximum. Swapping values.")
            self.config["MINIMUM"], self.config["MAXIMUM"] = self.config["MAXIMUM"], self.config["MINIMUM"]
    
    def configure_game_3(self) -> None:
        """Configure settings for Game 3 (buffer/timeout)"""
        print("\n=== Game 3 Configuration (Buffer/Timeout) ===")
        
        self.config["TRIGGER_WORD"] = self.get_input(
            "Trigger word", 
            self.config.get("TRIGGER_WORD", self.default_config["TRIGGER_WORD"])
        )
        
        self.config["BUFFER"] = self.get_int_input(
            "Buffer count (messages before trigger)", 
            self.config.get("BUFFER", self.default_config["BUFFER"])
        )
        
        if self.config["BUFFER"] < 0:
            print("Warning: Buffer count cannot be negative. Setting to default 5.")
            self.config["BUFFER"] = 5
    
    def configure_game_4(self) -> None:
        """Configure settings for Game 4 (dot counting)"""
        print("\n=== Game 4 Configuration (Dot Counting) ===")
        print("\nTrigger Conditions:")
        trigger_conditions = [
            "DOTS", "SPACES", "LETTERS", "DIGITS", 
            "WORDS", "ALPHABET", "OIIAI", "LOOPS"
        ]
        for i, condition in enumerate(trigger_conditions, 1):
            print(f"{i}. {condition}")
        
        while True:
            try:
              choice = self.get_int_input(
                  "Choose trigger condition (1-8)", 
                  trigger_conditions.index(self.config.get("TRIGGER_CONDITION", self.default_config["TRIGGER_CONDITION"])) + 1
              )
              if 1 <= choice <= 8:
                  self.config["TRIGGER_CONDITION"] = trigger_conditions[choice - 1]
                  break
              else:
                  print("Please enter a number between 1 and 8.")
            except ValueError:
              print("Please enter a valid number.")
        
        self.config["TRIGGER_CONDITION_VALUE"] = self.get_int_input(
            "Trigger condition value (attempts allowed)", 
            self.config.get("TRIGGER_CONDITION_VALUE", self.default_config["TRIGGER_CONDITION_VALUE"])
        )
    
    def configure_common(self) -> None:
        """Configure common settings"""
        print("\n=== Common Configuration ===")
        
        self.config["MESSAGE"] = self.get_input(
            "Trigger message", 
            self.config.get("MESSAGE", self.default_config["MESSAGE"])
        )
        
        count_user = self.get_input(
            "Count messages from the bot user? (TRUE/FALSE)", 
            self.config.get("COUNT_USER", self.default_config["COUNT_USER"])
        ).upper()
        
        self.config["COUNT_USER"] = "TRUE" if count_user == "TRUE" else "FALSE"
    
    def configure_hints(self) -> None:
        """Configure hints"""
        print("\n=== Hints Configuration ===")
        print("Configure hints to be sent at specific times")
        add_hints = self.get_input("Would you like to add hints? (y/n)", "n").lower()
        
        if add_hints == "y":
            self.config["HINTS"] = {}
            
            while True:
                hint_id = len(self.config["HINTS"]) + 1
                hint_text = self.get_input(f"Hint #{hint_id} text")
                
                if not hint_text:
                    break
                
                hint_date = self.get_input(f"Date for hint #{hint_id} (DD/MM/YYYY)", 
                                          datetime.now().strftime("%d/%m/%Y"))
                hint_time = self.get_input(f"Time for hint #{hint_id} (HH:MM)", "12:00")
                
                self.config["HINTS"][str(hint_id)] = [hint_text, hint_date, hint_time]
                
                more_hints = self.get_input("Add another hint? (y/n)", "n").lower()
                if more_hints != "y":
                    break
        else:
            self.config["HINTS"] = {}
    
    def run(self) -> None:
        """Run the configuration manager"""
        print("=== Telegram Bot Configuration Manager ===")
        
        # Check if config file exists
        existing_config = self.load_config()
        
        if existing_config:
            print(f"Found existing configuration file: {self.config_file}")
            use_existing = input("Would you like to use this configuration? (y/n) [y]: ").strip().lower()
            
            if use_existing != "n":
                self.config = existing_config
                print("Using existing configuration.")
                self.display_config()
                return
            
            use_as_base = input("Would you like to use it as a base for the new configuration? (y/n) [y]: ").strip().lower()
            
            if use_as_base != "n":
                self.config = existing_config
            else:
                self.config = {}
        
        # Select game type
        print("\n=== Game Selection ===")
        print("1. Trigger Word/Sticker")
        print("2. Target Message Count")
        print("3. Buffer/Timeout")
        print("4. Message Feature Counting")
        
        game_choice = self.get_int_input(
            "Select game type (1-4)", 
            self.config.get("GAME", self.default_config["GAME"])
        )
        
        if not 1 <= game_choice <= 4:
            print("Invalid choice. Defaulting to Game 1.")
            game_choice = 1
            
        self.config["GAME"] = game_choice
        
        # Configure specific game settings
        if game_choice == 1:
            self.configure_game_1()
        elif game_choice == 2:
            self.configure_game_2()
        elif game_choice == 3:
            self.configure_game_3()
        elif game_choice == 4:
            self.configure_game_4()
        
        # Configure common settings
        self.configure_common()
        
        # Configure hints
        self.configure_hints()
        
        # Save configuration
        save_config = input("Save configuration? (y/n) [y]: ").strip().lower()
        if save_config != "n":
            self.save_config()
            self.display_config()
    
    def display_config(self) -> None:
        """Display the current configuration"""
        print("\n=== Current Configuration ===")
        print(json.dumps(self.config, indent=2))


if __name__ == "__main__":
    # Add the datetime import for hints configuration
    import datetime
    
    config_manager = ConfigManager()
    config_manager.run()