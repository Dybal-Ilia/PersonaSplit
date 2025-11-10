import asyncio
import logging
from pathlib import Path
import yaml
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from langchain_core.messages import SystemMessage
from src.core.agents.agent import Agent
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
PRESETS_PATH = getenv('PRESETS_PATH')
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


@dp.message(Command("preset"))
async def cmd_preset(message: types.Message):
    with open(PRESETS_PATH, "r") as f:
        presets = yaml.safe_load(f)
    builder = ReplyKeyboardBuilder()
    for preset in presets.keys():
        builder.button(text=preset, callback_data=preset)
    builder.adjust(3)
    await message.answer("Some text here", reply_markup=builder.as_markup())


@dp.message()
async def cmd_echo(message:types.Message):
    with open(PRESETS_PATH, "r") as f:
        presets = yaml.safe_load(f)
    if message.text in presets.keys():
        await message.answer(f"Curent debators: {presets[message.text]["agents"]}")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())