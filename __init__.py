import os
import sys
import logging
from loguru import logger
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def logger_formater(record):
    record["extra"]["location"] = f"{record['name']}:{record['function']}:{record['line']}"
    return True


def logger_settings():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<italic><cyan>{time:DD-MM HH:mm:ss}</cyan></italic> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[location]: <57}</cyan> | "
            "<level>{message}</level>",
        filter=logger_formater
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    return logger


load_dotenv()
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

bot = Bot(
    token=TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
logger = logger_settings()