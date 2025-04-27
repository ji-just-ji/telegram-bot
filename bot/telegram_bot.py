import asyncio
from datetime import datetime
from pytz import timezone
from telethon import TelegramClient, events


class TelegramBot:
    """Main bot class that handles Telegram interactions"""
    
    def __init__(self, config, logger, game_controller, counter):
        self.config = config
        self.logger = logger
        self.game_controller = game_controller
        self.counter = counter
        
        # Initialize Telegram client
        self.client = TelegramClient('session_name', config.api_id, config.api_hash)
        
    async def start(self):
        """Start the bot and register handlers"""
        await self.client.start()
        self.logger.info("Client started successfully.")
        
        # Send introduction message
        await self.send_intro_message()
        
        # Register message handler
        self.client.add_event_handler(self.handle_new_message, events.NewMessage)
        
        # Start background tasks
        asyncio.create_task(self.send_hourly_message())
        asyncio.create_task(self.schedule_hint())
        
        # Run until disconnected
        await self.client.run_until_disconnected()
        
    async def handle_new_message(self, event):
        """Handle new messages in the chat"""
        # Target chat filter
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        if event.chat_id != chat_id:
            self.logger.info(f"Message from {event.chat_id} ignored.")
            return
        
        # Self message filter
        if not self.config.testing:
            if event.sender_id == int(self.config.my_id) and self.config.count_user == "FALSE":
                self.logger.info(f"Message from self ignored.")
                return
        
        # Ignore ignored users
        sender = await self.get_user_name(event)
        if sender in self.config.ignored_users:
            self.logger.info(f"Message from ignored user {sender} ignored.")
            return

        
        # Log message
        sender_name = await self.get_user_name(event)
        chat_name = await self.get_chat_name(event)
        self.logger.info(f"Message in {chat_name} from {sender_name}: {event.raw_text}")
        
        # Handle message based on game type
        self.counter.increment()
        
        if self.config.game == 1:
            if await self.game_controller.check_trigger(event):
                await self.send_game_1_win_message(event)
                await self.client.disconnect()
                
        elif self.config.game == 2:
            if await self.game_controller.check_target_count():
                await self.send_game_2_win_message(event)
                await self.client.disconnect()
                
        elif self.config.game == 3:
            if await self.game_controller.check_buffer(event):
                await self.send_game_3_win_message(event)
                await self.client.disconnect()
                
        elif self.config.game == 4:
            if self.game_controller.loser != "":
                if await self.game_controller.check_correct_answer(event):
                    await self.send_game_4_correct_answer_message(event)
                    await self.client.disconnect()
                    return
                    
            if await self.game_controller.check_trigger_condition(event):
                self.logger.info(f"Trigger condition value: {self.config.trigger_condition_value}")
                await self.send_game_4_trigger_message(event)
        else:
            self.logger.error("Invalid GAME value specified.")
            
        self.logger.info(f"Message count: {self.counter.message_count}")

    async def send_game_1_win_message(self, event):
        """Send win message for Game 1"""
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        await self.client.send_message(
            chat_id,
            f"{self.config.message}\nIt took {self.counter.message_count} messages to find this.\nThanks for playing!"
        )
        
    async def send_game_2_win_message(self, event):
        """Send win message for Game 2"""
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        name = await self.get_user_name(event)
        await self.client.send_message(
            chat_id,
            f"You've sent the {self.counter.message_count}th message. \nThanks @{name} for paying next supper too!"
        )
        self.logger.info(f"Target count reached: {self.counter.target_count} messages!")
        
    async def send_game_3_win_message(self, event):
        """Send win message for Game 3"""
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        name = await self.get_user_name(event)
        await self.client.send_message(
            chat_id,
            f"It's been too long since {self.config.trigger_word}, Thanks @{name} for paying next supper too!"
        )
        
    async def send_game_4_trigger_message(self, event):
        """Send trigger message for Game 4"""
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        user = await self.get_user_name(event)
        self.game_controller.loser = user
        await self.client.send_message(
            chat_id,
            f"{self.config.message}\nDamn @{user} why did you trigger the bot? \n"
            f"Next person to trigger the bot will take over as the loser.\n"
            f"If anyone can guess why the bot was triggered, you get a prize.\n"
            f"If you want to guess the answer, start your message with 'answer'. The bot will be quite lenient"
        )
        
    async def send_game_4_correct_answer_message(self, event):
        """Send correct answer message for Game 4"""
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        winner = await self.get_user_name(event)
        text = event.raw_text or ""
        
        if winner == self.game_controller.loser:
            if self.config.trigger_condition in ["DOTS", "SPACES", "LETTERS", "DIGITS", "WORDS", "LOOPS"]:
                message = (
                    f"No punishment for you @{winner}, you guessed the answer correctly! \n"
                    f"Thanks for playing!\n"
                    f"The answer was: {text}\n"
                    f"The bot was triggered by: {self.config.trigger_condition_value} {self.config.trigger_condition} in the message."
                )
            elif self.config.trigger_condition == "ALPHABET":
                message = (
                    f"No punishment for you @{winner}, you guessed the answer correctly! \n"
                    f"Thanks for playing!\n"
                    f"The answer was: {text}\n"
                    f"The bot was triggered by: The first letter in each word is in "
                    f"Alphabetical order with more than {self.config.trigger_condition_value} words."
                )
            else:
                message = (
                    f"No punishment for you @{winner}, you guessed the answer correctly! \n"
                    f"Thanks for playing!\n"
                    f"The answer was: {text}\n"
                    f"The bot was triggered by: The vowels in your message spell {self.config.trigger_condition}."
                )
        else:
            message = (

            )
            if self.config.trigger_condition in ["DOTS", "SPACES", "LETTERS", "DIGITS", "WORDS", "LOOPS"]:
                message = (
                    f"Correct! @{winner} guessed the answer correctly! \n"
                    f"Now @{self.game_controller.loser} owes you bbt! \n"
                    f"Thanks for playing!\n"
                    f"The answer was: {self.config.trigger_condition}\n"
                    f"The bot was triggered by: The first letter in each word is in "
                    f"Alphabetical order with more than {self.config.trigger_condition_value} words."
                
                )
            elif self.config.trigger_condition == "ALPHABET":
                message = (
                    f"Correct! @{winner} guessed the answer correctly! \n"
                    f"Now @{self.game_controller.loser} owes you bbt! \n"
                    f"Thanks for playing!\n"
                    f"The answer was: {self.config.trigger_condition}\n"
                    f"The bot was triggered by: {text}"
                )
            else:
                message = (
                    f"Correct! @{winner} guessed the answer correctly! \n"
                    f"Now @{self.game_controller.loser} owes you bbt! \n"
                    f"Thanks for playing!\n"
                    f"The answer was: {text}\n"
                    f"The bot was triggered by: The vowels in your message spell {self.config.trigger_condition}."
                )
        
        await self.client.send_message(chat_id, message)
        self.logger.info(f"Correct answer guessed: {text}")
        
    async def send_hourly_message(self):
        """Send hourly status message"""
        while True:
            await asyncio.sleep(3600)
            self.counter.save_message_count()
            await self.client.send_message(
                int(self.config.private_id),
                f"Game is still running! Current message count: {self.counter.message_count}"
            )
            self.logger.info("Hourly update sent.")
    
    async def schedule_hint(self):
        """Schedule hints based on configuration"""
        if not self.config.hints:
            self.logger.warning("No hints provided in the config.")
            return
          
        sg_tz = timezone('Asia/Singapore')
        for hint_id, hint_details in self.config.hints.items():
            try:
                hint_datetime = datetime.strptime(
                    f"{hint_details['DATE']} {hint_details['TIME']}", "%d/%m/%Y %H:%M"
                )
                hint_datetime = sg_tz.localize(hint_datetime)
                now = datetime.now(sg_tz)
                delay = (hint_datetime - now).total_seconds()

                if delay > 0:
                    asyncio.create_task(self.send_hint_after_delay(hint_details['HINT'], delay))
                    self.logger.info(f"Scheduled hint {hint_id} for {hint_datetime}.")
                else:
                    self.logger.warning(f"Hint {hint_id} is in the past and will not be scheduled.")
            except Exception as e:
                self.logger.error(f"Error scheduling hint {hint_id}: {e}")

    async def send_hint_after_delay(self, hint, delay):
        """Send a hint after a specified delay"""
        await asyncio.sleep(delay)
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        await self.client.send_message(chat_id, hint)
        self.logger.info(f"Hint sent: {hint}")
    
    async def get_user_name(self, event):
        """Get username of message sender"""
        try:
            sender = await event.get_sender()
            user_name = sender.username if sender else None
            return user_name
        except Exception as e:
            self.logger.error(f"Error getting user name: {e}")
            return None
    
    async def get_chat_name(self, event):
        """Get name of chat"""
        try:
            chat = await event.get_chat()
            self.logger.info(f"Chat name: {chat}")
            chat_name = chat.title if chat else None
            return chat_name
        except Exception as e:
            self.logger.error(f"Error getting chat name: {e}")
            return None
        
    async def send_intro_message(self):
        """Send introduction message to the chat"""
        chat_id = int(self.config.target_chat_id if not self.config.testing else self.config.private_id)
        if self.config.game == 1:
            message = (
                f"Hello! This is a bot to play a game. \n"
                f"There's a special word(s) or sticker. Don't trigger the bot\n"
                f"Have fun playing!"
            )
        elif self.config.game == 2:
            message = (
                f"Hello! This is a bot to play a game. \n"
                f"Send the {self.counter.target_count} message to lose!\n"
                f"Have fun playing!"
            )
        elif self.config.game == 3:
            message = (
                f"Hello! This is a bot to play a game. \n"
                f"Don't break the chain, say {self.config.trigger_word} in every {self.config.buffer} words or you lose.\n"
                f"Have fun playing!"
            )
        elif self.config.game == 4:
            message = (
                f"Hello! This is a bot to play a game. \n"
                f"The bot has a special trigger. Don't trigger the bot\n"
                f"Have fun playing!"
            )
        else:
            self.logger.error("Invalid GAME value specified.")
            return
        
        await self.client.send_message(
            chat_id,
            message
        )    
        
        self.logger.info("Introduction message sent.")