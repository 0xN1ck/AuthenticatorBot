import base64
import binascii
from datetime import timedelta

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter

from tgbot.keyboards.reply import generate_admin_menu
from tgbot.keyboards.inline import generate_user_key_menu, generate_users_menu, generate_keys_menu
from tgbot.keyboards.inline import MyCallbackData

from aiogram.fsm.context import FSMContext
from tgbot.misc.states import AdminMenuStates

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    admin_menu = await generate_admin_menu()
    await message.reply("Приветствую, админ!", reply_markup=admin_menu)


@admin_router.message(Command("reset_state"))
async def admin_start(message: Message, state: FSMContext):
    await state.clear()
    admin_menu = await generate_admin_menu()
    await message.answer("Состояние сброшено!", reply_markup=admin_menu)


@admin_router.message(lambda message: message.text.startswith("➕\u200BДобавить"))
async def handle_add_button(message: Message):
    add_menu = await generate_user_key_menu('add')
    await message.answer("Выберите пункт меню для добавления:", reply_markup=add_menu)


@admin_router.message(lambda message: message.text.startswith("➖\u200BУдалить"))
async def handle_delete_button(message: Message):
    delete_menu = await generate_user_key_menu('delete')
    await message.answer("Выберите пункт меню для удаления:", reply_markup=delete_menu)


@admin_router.message(lambda message: message.text.startswith("👁️\u200BПросмотр"))
async def handle_view_button(message: Message):
    view_menu = await generate_user_key_menu('view')
    await message.answer("Выберите пункт меню для просмотра:", reply_markup=view_menu)


@admin_router.callback_query(StateFilter(None), MyCallbackData.filter())
async def handle_my_callback_query(callback_query: CallbackQuery, callback_data: MyCallbackData,
                                   state: FSMContext, repo: RequestsRepo):
    action = callback_data.action
    target = callback_data.target

    await callback_query.answer()

    if action == 'add':
        if target == 'user':
            await callback_query.message.answer(f"Вы выбрали добавление пользователя.\n\n"
                                                f"Шаблон ввода данных для примера:\n"
                                                f"<b>user_id:</b> 11111111\n"
                                                f"<b>username:</b> Username\n"
                                                f"<b>full_name:</b> Firstname Lastname\n"
                                                f"<b>chat_id:</b> 11111111 (должен был написать бот при попытке его использовать)")
            await state.set_state(AdminMenuStates.waiting_add_user_data)
        elif target == 'key':
            await callback_query.message.answer(f"<i>Вы выбрали добавление ключа.</i>\n"
                                                f"<b>Введите имя:</b> <i>например,</i> <b>ByBit</b>\n"
                                                f"<b>Обязательно убедитесь, что это имя свободно!</b>")
            await state.set_state(AdminMenuStates.waiting_add_key_name_data)

    elif action == 'delete':
        if target == 'user':
            delete_user_menu = await generate_users_menu(action=action, target=target, repo=repo)
            await callback_query.message.answer(f"Вы выбрали удаление пользователя.",
                                                reply_markup=delete_user_menu)
            await state.set_state(AdminMenuStates.waiting_delete_user_data)
        elif target == 'key':
            delete_key_menu = await generate_keys_menu(action=action, target=target, repo=repo)
            await callback_query.message.answer(f"Вы выбрали удаление ключа.", reply_markup=delete_key_menu)
            await state.set_state(AdminMenuStates.waiting_delete_key_data)

    elif action == 'view':
        if target == 'user':
            view_user_menu = await generate_users_menu(action=action, target=target, repo=repo)
            await callback_query.message.answer(f"Вы выбрали просмотр пользователя.",
                                                reply_markup=view_user_menu)
            await state.set_state(AdminMenuStates.waiting_view_user_data)
        elif target == 'key':
            view_key_menu = await generate_keys_menu(action=action, target=target, repo=repo)
            await callback_query.message.answer(f"Вы выбрали просмотр ключа.", reply_markup=view_key_menu)
            await state.set_state(AdminMenuStates.waiting_view_key_data)


@admin_router.message(AdminMenuStates.waiting_add_user_data)
async def handle_my_user_data_add(message: Message, state: FSMContext, repo: RequestsRepo):
    user_data = message.text.split('\n')

    user_info = {}
    expected_keys = ["user_id", "username", "full_name", "chat_id"]

    for item in user_data:
        try:
            key, value = item.split(': ', 1)
            key = key.lower()
            if key not in expected_keys:
                raise ValueError(f"Неверный ключ: {key}")
            user_info[key] = value.strip()
        except ValueError as e:
            await message.answer(f"<b>Ошибка:</b>\n"
                                 f"<i>Ваше сообщение не соответствует шаблону или</i>\n\n"
                                 f"Шаблон ввода данных для примера:\n"
                                 f"<b>user_id:</b> 11111111\n"
                                 f"<b>username:</b> Username\n"
                                 f"<b>full_name:</b> Firstname Lastname\n"
                                 f"<b>chat_id:</b> 11111111\n (должен был написать бот при попытке его использовать)")
            return

    try:
        user = await repo.users.get_or_create_user(user_id=int(user_info['user_id']),
                                                   username=user_info['username'],
                                                   full_name=user_info['full_name'])
        if user:
            await message.answer(
                f"<i>Пользователь</i> <b>{user_info['username']}</b> <i>успешно добавлен в базу данных</i>.\n")
            await message.bot.send_message(chat_id=int(user_info['chat_id']),
                                           text="Администратор дал Вам доступ к боту\n"
                                                "Выполните команду /start")
        else:
            await message.answer(f"Ошибка при добавлении пользователя. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении пользователя:\n{str(e)}")

    await state.clear()


@admin_router.callback_query(AdminMenuStates.waiting_delete_user_data, MyCallbackData.filter())
async def handle_my_user_data_delete(callback_query: CallbackQuery, callback_data: MyCallbackData, state: FSMContext,
                                     repo: RequestsRepo):
    user_id = int(callback_data.user_id)
    username = callback_data.username

    existing_user = await repo.users.get_user_by_id(user_id)
    if existing_user:
        await repo.users.delete_user_by_id(user_id)
        await callback_query.answer()
        await callback_query.message.answer(f"<i>Вы успешно удалили пользователя</i> <b>{username}</b>.\n\n")
    else:
        await callback_query.answer(f"Ошибка: Пользователь {username} не найден.")

    await state.clear()


@admin_router.callback_query(AdminMenuStates.waiting_view_user_data, MyCallbackData.filter())
async def handle_my_user_data_view(callback_query: CallbackQuery, callback_data: MyCallbackData, state: FSMContext,
                                   repo: RequestsRepo):
    data_user = await repo.users.get_user_by_id(int(callback_data.user_id))

    await callback_query.answer()

    created_at = (data_user[0].created_at + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    text = (f"<i>Пользователь:</i> <b>{data_user[0].username}</b>\n"
            f"<i>- ID:</i> <b>{data_user[0].user_id}</b>\n"
            f"<i>- Имя:</i> <b>{data_user[0].full_name}</b>\n"
            f"<i>- Добавлен:</i> <b>{str(created_at)}</b>")

    await callback_query.message.edit_text(text)
    await state.clear()


@admin_router.message(AdminMenuStates.waiting_add_key_name_data)
async def handle_my_key_name_data_add(message: Message, state: FSMContext, repo: RequestsRepo):
    market_name = message.text.strip()
    market_key = ""  # pyotp.random_base32()

    if await repo.markets.get_market_by_name(market_name):
        await message.answer(f"Ключ c именем <b>{market_name}</b> уже существует.\n"
                             f"<b>Пожалуйста, попробуйте еще раз. Напишите другое свободное имя.</b>")
        return

    await state.update_data(market_name=market_name, market_key=market_key)
    await message.answer(
        f"<i>Имя</i> <b>{market_name}</b> <i>успешно прошло проверку</i>.\n"
        f"<i>Теперь введите секрутный ключ для</i> <b>{market_name}</b>.\n"
        f"<b>Секретный ключ обязательно должен соответствовать формату base32</b>\n")

    await state.set_state(AdminMenuStates.waiting_add_key_secret_data)


@admin_router.message(AdminMenuStates.waiting_add_key_secret_data)
async def handle_my_key_secret_data_add(message: Message, state: FSMContext, repo: RequestsRepo):
    key_data = await state.get_data()
    key_data['market_key'] = message.text.strip()

    try:
        base64.b32decode(key_data['market_key'], casefold=True)
    except binascii.Error:
        await message.answer(f"Секретный ключ <b>{key_data['market_key']} некорректен.</b>\n"
                             f"Пожалуйста, введите секртный ключ еще раз.\n"
                             f"<b>Секретный ключ обязательно должен соответствовать формату base32!</b>")
        return

    await state.update_data(market_key=key_data['market_key'])

    try:
        key = await repo.markets.get_or_create_market(market_name=key_data['market_name'],
                                                      market_key=key_data['market_key'])
        if key:
            await message.answer(
                f"<i>Ключ</i> <b>{key_data['market_name']}</b> <i>успешно добавлен в базу данных</i>.\n")
        else:
            await message.answer(
                f"Ошибка при создании ключа {key_data['market_name']}. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании ключа:\n{str(e)}")

    await state.clear()


@admin_router.callback_query(AdminMenuStates.waiting_delete_key_data, MyCallbackData.filter())
async def handle_my_key_data_delete(callback_query: CallbackQuery, callback_data: MyCallbackData, state: FSMContext,
                                    repo: RequestsRepo):
    market_name = str(callback_data.market_name)

    existing_key = await repo.markets.get_market_by_name(market_name)

    if existing_key:
        await repo.markets.delete_market_by_name(market_name)
        await callback_query.answer()
        await callback_query.message.answer(f"<i>Вы успешно удалили ключ</i> <b>{market_name}</b>.\n\n")
    else:
        await callback_query.answer(f"Ошибка: Ключ {market_name} не найден.")

    await state.clear()


@admin_router.callback_query(AdminMenuStates.waiting_view_key_data, MyCallbackData.filter())
async def handle_my_key_data_view(callback_query: CallbackQuery, callback_data: MyCallbackData, state: FSMContext,
                                  repo: RequestsRepo):
    data_key = await repo.markets.get_market_by_name(str(callback_data.market_name))

    await callback_query.answer()

    created_at = (data_key.created_at + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    text = (f"<i>Название:</i> <b>{str(data_key.market_name)}</b>\n"
            f"<i>- Секретный ключ:</i> <code>{str(data_key.market_key)}</code>\n"
            f"<i>- Создан:</i> <b>{str(created_at)}</b>")

    await callback_query.message.edit_text(text)
    await state.clear()
