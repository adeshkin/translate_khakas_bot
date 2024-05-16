import asyncio
import logging
import sys
from typing import Any, Dict
import requests
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import TOKEN, kjh2ru_url, ru2kjh_url, kjh_tts_url

form_router = Router()


class Form(StatesGroup):
    task = State()
    user_input = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.task)
    await message.answer(
        "Изеннер!\nНиме идерге сағынчазар?\nЧто хотите сделать?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Перевести текст с хакасского на русский")],
                [KeyboardButton(text="Перевести текст с русского на хакасский")],
                [KeyboardButton(text="Озвучить текст на хакасском языке")],
            ],
            resize_keyboard=True,
        ),
    )


# @form_router.message(Command("cancel"))
# @form_router.message(F.text.casefold() == "cancel")
# async def cancel_handler(message: Message, state: FSMContext) -> None:
#     """
#     Allow user to cancel any action
#     """
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     logging.info("Cancelling state %r", current_state)
#     await state.clear()
#     await message.answer(
#         "Cancelled.",
#         reply_markup=ReplyKeyboardRemove(),
#     )


# @form_router.message(Form.task)
# async def process_name(message: Message, state: FSMContext) -> None:
#     await state.update_data(name=message.text)
#     await state.set_state(Form.like_bots)
#     await message.answer(
#         f"Nice to meet you, {html.quote(message.text)}!\nDid you like to write bots?",
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text="Yes"),
#                     KeyboardButton(text="No"),
#                 ]
#             ],
#             resize_keyboard=True,
#         ),
#     )


# @form_router.message(Form.like_bots, F.text.casefold() == "no")
# async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     await state.clear()
#     await message.answer(
#         "Not bad not terrible.\nSee you soon.",
#         reply_markup=ReplyKeyboardRemove(),
#     )
#     await show_summary(message=message, data=data, positive=False)
#
#
# @form_router.message(Form.like_bots, F.text.casefold() == "yes")
# async def process_like_write_bots(message: Message, state: FSMContext) -> None:
#     await state.set_state(Form.language)
#
#     await message.reply(
#         "Cool! I'm too!\nWhat programming language did you use for it?",
#         reply_markup=ReplyKeyboardRemove(),
#     )
#
#
# @form_router.message(Form.like_bots)
# async def process_unknown_write_bots(message: Message) -> None:
#     await message.reply("I don't understand you :(")
#

@form_router.message(Form.task)
async def process_task(message: Message, state: FSMContext) -> None:
    data = await state.update_data(task=message.text)
    task = data['task']

    if task == 'Перевести текст с хакасского на русский':
        await state.set_state(Form.user_input)
        await message.answer("Введите текст на хакасском языке", reply_markup=ReplyKeyboardRemove())
    elif task == 'Перевести текст с русского на хакасский':
        await state.set_state(Form.user_input)
        await message.answer("Введите текст на русском языке", reply_markup=ReplyKeyboardRemove())
    elif task == 'Озвучить текст на хакасском языке':
        await state.set_state(Form.user_input)
        await message.answer("ВЫ: Озвучить текст на хакасском языке", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Некорректная команда", reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.user_input)
async def process_user_input(message: Message, state: FSMContext) -> None:
    data = await state.update_data(task=message.text)
    task = data['task']
    user_input = data['user_input']

    if task == 'Перевести текст с хакасского на русский':
        await translate_kjh2ru(message=message, state=state, text=user_input)
    elif task == 'Перевести текст с русского на хакасский':
        await translate_kjh2ru(message=message, state=state, text=user_input)
    elif task == 'Озвучить текст на хакасском языке':
        await state.set_state(Form.user_input)
        await message.answer("ВЫ: Озвучить текст на хакасском языке", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Некорректная команда", reply_markup=ReplyKeyboardRemove())


async def translate_kjh2ru(message: Message, state: FSMContext, text: str) -> None:
    translation = requests.get(kjh2ru_url, params={'text': text}).text
    await message.reply(text=translation, reply_markup=ReplyKeyboardRemove())


async def translate_ru2kjh(message: Message, state: FSMContext, text: str) -> None:
    translation = requests.get(ru2kjh_url, params={'text': text}).text
    await message.reply(text=translation, reply_markup=ReplyKeyboardRemove())






# async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
#     name = data["name"]
#     language = data.get("language", "<something unexpected>")
#     text = f"I'll keep in mind that, {html.quote(name)}, "
#     text += (
#         f"you like to write bots with {html.quote(language)}."
#         if positive
#         else "you don't like to write bots, so sad..."
#     )
#     await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())