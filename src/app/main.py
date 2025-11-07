import asyncio
import logging
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from langchain_core.messages import SystemMessage
from src.core.agents.agent import Agent
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("debate"))
async def cmd_start(message: types.Message):
    user_topic = message.text
    rationalist = Agent("rationalist")
    humanist = Agent("humanist")
    debate_history = [SystemMessage(f"Orchestrator said: You are to debate on {user_topic}")]
    rationalist_response = rationalist.run(topic=user_topic, messages=debate_history)
    
    await message.answer(rationalist.history[-1])

    debate_history.append(rationalist_response["messages"][-1])

    humanist_response = humanist.run(topic=user_topic, messages=debate_history)
    await message.answer(humanist.history[-1])

    debate_history.append(humanist_response["messages"][-1])



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())