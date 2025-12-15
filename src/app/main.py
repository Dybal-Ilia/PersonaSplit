import asyncio
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
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
PRESETS_PATH = getenv('PRESETS_PATH') or "/app/src/core/presets/presets.yaml"
try:
    from os.path import exists
    if not exists(PRESETS_PATH):
        PRESETS_PATH = "/app/src/core/presets/presets.yaml"
except Exception:
    PRESETS_PATH = "/app/src/core/presets/presets.yaml"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
presets = load_yaml(PRESETS_PATH)


async def _start_debate(message: types.Message, topic: str, preset: str | None, state: FSMContext):
    user_data = await state.get_data()
    chosen_preset = preset or user_data.get("selected_preset", "classic")
    try:
        agents_list = presets[chosen_preset]["agents"]
    except Exception:
        await message.answer("An error occurred. Preset is not found. Switching to 'classic'.")
        chosen_preset = "classic"
        agents_list = presets[chosen_preset]["agents"]

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
            response_message = patch.get("next_speaker")
            if response_message:
                await message.answer(f"{response_message} is now to speak")

        if patch.get("history_patch"):
            await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            response_message = patch["history_patch"]
            persona_name = node_name.capitalize()
            full_text = f"**{persona_name}**\n{response_message.content.split(':', maxsplit=1)[-1]}"
            await message.answer(full_text)

        elif node_name == "Judge":
            judge_decision = patch.get("judge_decision")
            if judge_decision:
                await message.answer(f"**Judges Verdict:**\n{judge_decision.content}")

@dp.message(Command("debate"))
async def cmd_debate(message: types.Message, state: FSMContext):
    # Backward compatibility: /debate <topic>
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /debate <topic>")
        return
    topic = parts[1].strip()
    data = await state.get_data()
    preset = data.get("selected_preset")
    await _start_debate(message, topic, preset, state)


@dp.message()
async def topic_or_other(message: types.Message, state: FSMContext):
    if not message.text:
        return
    if message.text.startswith('/'):
        return

    text = message.text.strip()

    # If user typed a preset name (legacy reply keyboard), store and confirm
    if text in presets:
        await state.update_data(selected_preset=text)
        await message.answer(
            f"Chosen preset is {text}\n\nThe debaters are: {', '.join(presets[text]['agents'])}",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # Treat text as a topic and ask to choose preset via inline buttons
    await state.update_data(pending_topic=text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"select_preset:{name}")]
        for name in presets.keys()
    ])
    await message.answer("Choose the preset", reply_markup=kb)


@dp.callback_query(F.data.startswith("select_preset:"))
async def on_preset_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    preset = callback.data.split(":", 1)[1]
    data = await state.get_data()
    topic = data.get("pending_topic")
    if not topic:
        await callback.message.answer("Please send a topic first.")
        return

    await state.update_data(selected_preset=preset)
    # Hide buttons from the selection message
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(f"Starting debate on: {topic} (preset: {preset})")
    await _start_debate(callback.message, topic, preset, state)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())