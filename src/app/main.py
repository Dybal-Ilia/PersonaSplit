import asyncio
import contextlib
from os import getenv
from uuid import uuid4

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ChatAction
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv

from src.core.agents.orchestration import GraphFactory
from src.core.schemas.state import ChatState
from src.utils.loaders import load_yaml

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
PRESETS_PATH = getenv("PRESETS_PATH") or "/app/src/core/presets/presets.yaml"
try:
    from os.path import exists

    if not exists(PRESETS_PATH):
        PRESETS_PATH = "/app/src/core/presets/presets.yaml"
except Exception:
    PRESETS_PATH = "/app/src/core/presets/presets.yaml"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
presets = load_yaml(PRESETS_PATH)


async def _start_debate(
    message: types.Message, topic: str, preset: str | None, state: FSMContext
):
    user_data = await state.get_data()
    chosen_preset = preset or user_data.get("selected_preset", "classic")
    try:
        agents_list = presets[chosen_preset]["agents"]
    except Exception:
        await message.answer(
            "An error occurred. Preset is not found. Switching to 'classic'."
        )
        chosen_preset = "classic"
        agents_list = presets[chosen_preset]["agents"]

    graph = GraphFactory(agents_list=agents_list)
    app = graph.build_graph()
    initial_state = ChatState(
        topic=topic, debators=agents_list, session_id=str(uuid4())
    )

    async for event in app.astream(initial_state, config={"recursion_limit": 100}):
        node_name, patch = list(event.items())[0]
        if node_name == "Orchestrator":
            continue

        if patch.get("history_patch"):
            await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            response_message = patch["history_patch"]
            persona_name = node_name.capitalize()
            full_text = f"**{persona_name}**\n{response_message.content.split(':', maxsplit=1)[-1]}"
            await message.answer(text=full_text, parse_mode="Markdown")

        elif node_name == "Judge":
            judge_decision = patch.get("judge_decision")
            if judge_decision:
                await message.answer(
                    text=f"**Judges Verdict:**\n{judge_decision.content}",
                    parse_mode="Markdown",
                )


@dp.message(Command("debate"))
async def cmd_debate(message: types.Message, state: FSMContext):
    # Backward compatibility: /debate <topic>
    if not message.text:
        await message.answer("Usage: /debate <topic>")
        return
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
    if message.text.startswith("/"):
        return

    text = message.text.strip()

    # If user typed a preset name (legacy reply keyboard), store and confirm
    if text in presets:
        await state.update_data(selected_preset=text)
        await message.answer(
            f"Chosen preset is {text}\n\nThe debaters are: {', '.join(presets[text]['agents'])}",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    # Treat text as a topic and ask to choose preset via inline buttons
    await state.update_data(pending_topic=text)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"select_preset:{name}")]
            for name in presets
        ]
    )
    await message.answer("Choose the preset", reply_markup=kb)


@dp.callback_query(F.data.startswith("select_preset:"))
async def on_preset_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if not callback.data:
        return
    preset = callback.data.split(":", 1)[1]
    data = await state.get_data()
    topic = data.get("pending_topic")
    if not topic:
        if callback.message:
            await callback.message.answer("Please send a topic first.")
        return

    await state.update_data(selected_preset=preset)
    msg = callback.message
    if msg is None or not isinstance(msg, types.Message):
        return
    # Hide buttons from the selection message
    with contextlib.suppress(Exception):
        await msg.edit_reply_markup(reply_markup=None)
    await msg.answer(f"Starting debate on: {topic} (preset: {preset})")
    await _start_debate(msg, topic, preset, state)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
