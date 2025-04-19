from config.config import Config
from games.controller import GameController
from bot.telegram_bot import TelegramBot
from services.embedding import EmbeddingService
from services.counter import MessageCounter
from utils.logger import Logger


import asyncio

async def main():
    """Main entry point"""
    # Initialize components
    config = Config()
    logger_instance = Logger()
    logger = logger_instance.logger
    
    embedding_service = EmbeddingService(config.openai_key)
    embedding_service.initialize_embeddings(config.game, config.trigger_condition)
    
    counter = MessageCounter(config.min_num, config.max_num, logger)
    game_controller = GameController(config, embedding_service, counter, logger)
    
    bot = TelegramBot(config, logger, game_controller, counter)
    
    # Start bot
    await bot.start()


if __name__ == '__main__':
    asyncio.run(main())