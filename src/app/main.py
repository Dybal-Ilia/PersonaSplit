import asyncio
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from src.utils.logger import logger
from src.utils.loaders import load_yaml
from src.core.agents.orchestration import GraphFactory
from src.core.schemas.state import ChatState
from uuid import uuid4

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
PRESETS_PATH = getenv('PRESETS_PATH')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
presets = load_yaml(PRESETS_PATH)
TELEGRAM_MAX_LENGTH = 4096

@dp.message(Command("debate"))
async def cmd_start(message: types.Message, state:FSMContext):
    topic = message.text.split(maxsplit=1)[-1]
    user_data = await state.get_data()
    preset = user_data.get("selected_preset", "classic_preset")
    try:
        agents_list = presets[preset]["agents"]
    except KeyError:
        await message.answer("An error occurred. Preset is not found. Switching to 'classic'.")
        agents_list = presets["classic_preset"]["agents"]
    await message.answer(f"Got You! (Preset: {preset})\nPreparing Debators...")
    graph = GraphFactory(agents_list=agents_list)
    app = graph.build_graph()
    initial_state = ChatState(
        topic=topic,
        debators=agents_list,
        session_id=str(uuid4())
        )

    async for event in app.astream(initial_state, config={"recursion_limit": 100}):
        node_name, patch = list(event.items())[0]
        if node_name == "Orchestrator":
            response_message = patch["next_speaker"]
            await message.answer(f"{response_message} is now to speak")

        if "history_patch" in patch and patch["history_patch"]:
            await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            response_message = patch["history_patch"]
            persona_name = node_name.capitalize()
            full_text = f"**{persona_name}**\n{response_message.content.split(':', maxsplit=1)[-1]}"
            await message.answer(full_text)

        elif node_name == "Judge":
            judge_decision = patch["judge_decision"]

            await message.answer(f"**Judges Verdict:**\n{judge_decision.content}")


@dp.message(Command("preset"))
async def cmd_preset(message: types.Message):

    presets = load_yaml(path=PRESETS_PATH)
    builder = ReplyKeyboardBuilder()
    for preset in presets.keys():
        builder.button(text=preset, callback_data=preset)
    builder.adjust(4)
    await message.answer("Choose one of available presets below",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text.in_(presets.keys()))
async def preset_chosen(message: types.Message, state:FSMContext):
    chosen = message.text
    await state.update_data(selected_preset=chosen)

    await message.answer(
        f"Chosen preset is {chosen}\n\nThe debators are: {", ".join(presets[chosen]["agents"])}",
        reply_markup=ReplyKeyboardRemove()
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())