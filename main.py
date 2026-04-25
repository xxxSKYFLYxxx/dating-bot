import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    looking_for = State()
    description = State()
    photo = State()



def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Искать", callback_data="search")],
        [InlineKeyboardButton(text="👤 Моя анкета", callback_data="my_profile")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit")],
        [InlineKeyboardButton(text="❌ Удалить анкету", callback_data="delete")]
    ])
    return keyboard


def get_gender_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужчина", callback_data="gender_male")],
        [InlineKeyboardButton(text="👩 Женщина", callback_data="gender_female")]
    ])
    return keyboard


def get_looking_for_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужчин", callback_data="looking_male")],
        [InlineKeyboardButton(text="👩 Женщин", callback_data="looking_female")],
        [InlineKeyboardButton(text="👥 Всех", callback_data="looking_both")]
    ])
    return keyboard


def get_like_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Нравится", callback_data=f"like_{user_id}"),
         InlineKeyboardButton(text="👉 Далее", callback_data=f"next_{user_id}")],
        [InlineKeyboardButton(text="❌ Выйти", callback_data="stop_search")]
    ])
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user and user[7]:  # is_active
        await message.answer("Привет! Ты уже зарегистрирован.", reply_markup=get_main_keyboard())
    else:
        await message.answer("Привет! Давай создадим твою анкету.\n\nКак тебя зовут?")
        await state.set_state(Form.name)


@dp.message(Form.name)
async def form_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def form_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 16 or age > 100:
            await message.answer("Возраст должен быть от 16 до 100. Попробуй ещё раз.")
            return
        await state.update_data(age=age)
        await message.answer("Кто ты?", reply_markup=get_gender_keyboard())
        await state.set_state(Form.gender)
    except ValueError:
        await message.answer("Введи число.")


@dp.callback_query(Form.gender)
async def form_gender(callback: types.CallbackQuery, state: FSMContext):
    gender = callback.data.replace("gender_", "")
    await state.update_data(gender=gender)
    await callback.message.answer("Кого ты ищешь?", reply_markup=get_looking_for_keyboard())
    await state.set_state(Form.looking_for)
    await callback.answer()


@dp.callback_query(Form.looking_for)
async def form_looking_for(callback: types.CallbackQuery, state: FSMContext):
    looking_for = callback.data.replace("looking_", "")
    await state.update_data(looking_for=looking_for)
    await callback.message.answer("Напиши немного о себе:")
    await state.set_state(Form.description)
    await callback.answer()


@dp.message(Form.description)
async def form_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Отправь своё фото:")
    await state.set_state(Form.photo)


@dp.message(Form.photo, F.photo)
async def form_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    
    db.add_user(
        user_id,
        data['name'],
        data['age'],
        data['gender'],
        data['looking_for'],
        data['description'],
        photo_file_id
    )
    
    await message.answer("Анкета создана! 🎉", reply_markup=get_main_keyboard())
    await state.clear()


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user[7]:
        await message.answer("У тебя нет анкеты. Напиши /start для регистрации.")
        return
    
    text = f"👤 {user[1]}, {user[2]} лет\n\n{user[5]}"
    
    if user[6]:
        await message.answer_photo(user[6], caption=text)
    else:
        await message.answer(text)


@dp.message(Command("search"))
async def cmd_search(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user[7]:
        await message.answer("У тебя нет анкеты. Напиши /start для регистрации.")
        return
    
    profiles = db.get_active_profiles(user_id, user[4])  # looking_for
    
    if not profiles:
        await message.answer("Нет анкет для просмотра. Попробуй позже!")
        return
    
    profile_id = profiles[0]
    profile = db.get_user(profile_id)
    
    text = f"👤 {profile[1]}, {profile[2]} лет\n\n{profile[5]}"
    
    if profile[6]:
        await message.answer_photo(profile[6], caption=text, reply_markup=get_like_keyboard(profile_id))
    else:
        await message.answer(text, reply_markup=get_like_keyboard(profile_id))


@dp.callback_query(F.data.startswith("like_"))
async def callback_like(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    liked_user_id = int(callback.data.replace("like_", ""))
    
    db.add_like(user_id, liked_user_id)
    
    if db.check_mutual_like(user_id, liked_user_id):
        chat_id = db.create_chat(user_id, liked_user_id)
        
        await bot.send_message(user_id, "Это взаимная симпатия! 💕 Теперь вы можете общаться анонимно.")
        await bot.send_message(liked_user_id, "Это взаимная симпатия! 💕 Теперь вы можете общаться анонимно.")
    
    await callback.message.answer("❤️ лайк отправлен! Смотри дальше:", reply_markup=get_main_keyboard())
    await callback.answer()


@dp.callback_query(F.data.startswith("next_"))
async def callback_next(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    profiles = db.get_active_profiles(user_id, user[4])
    
    if not profiles:
        await callback.message.answer("Нет больше анкет.")
        await callback.answer()
        return
    
    profile_id = profiles[0]
    profile = db.get_user(profile_id)
    
    text = f"👤 {profile[1]}, {profile[2]} лет\n\n{profile[5]}"
    
    if profile[6]:
        await callback.message.answer_photo(profile[6], caption=text, reply_markup=get_like_keyboard(profile_id))
    else:
        await callback.message.answer(text, reply_markup=get_like_keyboard(profile_id))
    
    await callback.answer()


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    user_id = message.from_user.id
    db.deactivate_user(user_id)
    await message.answer("Анкета удалена. Напиши /start чтобы создать новую.")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user[7]:
        await message.answer("Напиши /start для начала.")
        return
    
    partner = db.get_chat_partner(user_id)
    
    if partner:
        await bot.send_message(partner, message.text)
    else:
        await message.answer("У тебя нет активного чата. Найди совпадение!", reply_markup=get_main_keyboard())


async def main():
    db.init_db()
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())