import asyncio
import logging
import sys
from typing import Any, Dict

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

from config import TOKEN

form_router = Router()


class Form(StatesGroup):
    task = State()


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
        await message.answer("Введите текст на хакасском языке", reply_markup=ReplyKeyboardRemove())
    elif task == 'Перевести текст с русского на хакасский':
        await message.answer("Введите текст на русском языке", reply_markup=ReplyKeyboardRemove())
    elif task == 'Озвучить текст на хакасском языке':
        await message.answer("ВЫ: Озвучить текст на хакасском языке", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Некорректная команда", reply_markup=ReplyKeyboardRemove())


async def translate_khakas_russian(message: Message, state: FSMContext, from_skip: bool = False, to_correct: bool = False) -> None:
    data = await state.get_data()

    # allow user to correct his answer
    if to_correct:
        input_sent = data['input_sent']
        await state.set_state(Form.user_sent)

        # if user skip, just change sentence
        if from_skip:
            await message.edit_text(f'{input_sent}', reply_markup=skip_change_keyboard)
        else:
            await message.answer('*Переведите с хакасского языка на русский:*', reply_markup=ReplyKeyboardRemove(),
                                 parse_mode='MarkdownV2')
            await message.answer(f'{input_sent}', reply_markup=skip_change_keyboard)
    else:
        input_sent = prepare_sent_for_translation(language='khakas')
        if input_sent is None:
            await state.update_data(available_translate=False)
            await message.answer('*Задания данного типа закончились\.*', parse_mode='MarkdownV2')
            await choose_task_type(message=message, state=state)
        else:
            await state.update_data(input_sent=input_sent)

            await state.set_state(Form.user_sent)

            # if user skip, just change sentence
            if from_skip:
                await message.edit_text(f'{input_sent}', reply_markup=skip_change_keyboard)
            else:
                await message.answer('*Переведите с хакасского языка на русский:*', reply_markup=ReplyKeyboardRemove(),
                                     parse_mode='MarkdownV2')
                await message.answer(f'{input_sent}', reply_markup=skip_change_keyboard)

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