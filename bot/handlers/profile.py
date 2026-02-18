from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from keyboards.inline_profile import edit_profile_keyboard
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from states.profile_state import ProfileState

from bot.database.base import User

router = Router()

@router.message(F.text.in_(set(("Profile", "  Profile"))))
async def profile_entry(message: Message, state: FSMContext, session: AsyncSession):
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    if user:
        await message.answer(
            f"📋 Your profile\n"
            f"Name: {user.username}\n"
            f"City: {user.city}\n"
            f"Hobbies: {user.hobbies}\n"
            f"Age: {user.age}\n\n"
            f"To edit your profile, use /edit_profile"
        )
    else:
        await message.answer("You don't have a profile yet. Let's create one!\nWhat is your name?", reply_markup=edit_profile_keyboard())
        await state.set_state(ProfileState.name)

@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    result = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = result.scalar_one_or_none()
    if not user:
        await callback.message.answer("You don't have a profile yet. Use the Profile button to create one.")
        await callback.answer()
        return
    await state.update_data(
        name=user.username,
        city=user.city,
        hobbies=user.hobbies,
        age=user.age
    )
    await callback.message.answer("Let's edit your profile. What is your new name?")
    await state.set_state(ProfileState.name)
    await callback.answer()

@router.message(ProfileState.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    await message.answer("Thanks! Now tell me your city:")
    await state.set_state(ProfileState.city)

@router.message(ProfileState.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    await state.update_data(city=city)
    await message.answer("Great! What are your hobbies?")
    await state.set_state(ProfileState.hobbies)

@router.message(ProfileState.hobbies)
async def process_hobbies(message: Message, state: FSMContext):
    hobbies = message.text.strip()
    await state.update_data(hobbies=hobbies)
    await message.answer("Finally, how old are you? (enter a number)")
    await state.set_state(ProfileState.age)

@router.message(ProfileState.age)
async def process_age(message: Message, state: FSMContext, session: AsyncSession):
    try:
        age = int(message.text.strip())
    except ValueError:
        await message.answer("Please enter a valid number for your age.")
        return
    await state.update_data(age=age)
    data = await state.get_data()
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(tg_id=message.from_user.id)
        session.add(user)
    user.username = data.get("name")
    user.city = data.get("city")
    user.hobbies = data.get("hobbies")
    user.age = data.get("age")
    await session.commit()
    await message.answer(
        f"✅ Profile saved!\n"
        f"Name: {user.username}\n"
        f"City: {user.city}\n"
        f"Hobbies: {user.hobbies}\n"
        f"Age: {user.age}"
    )
    await state.clear()

@router.message(F.text == "Cancel")
async def cancel_profile(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Profile setup cancelled.")
