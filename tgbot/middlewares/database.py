from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        # async with self.session_pool() as session:
        #     repo = RequestsRepo(session)
        #
        #     user = await repo.users.get_or_create_user(
        #         user_id=event.from_user.id,
        #         full_name=event.from_user.full_name,
        #         # event.from_user.language_code,
        #         username=event.from_user.username
        #     )
        #
        #     data["session"] = session
        #     data["repo"] = repo
        #     data["user"] = user
        #
        #     result = await handler(event, data)

        async with self.session_pool() as session:
            repo = RequestsRepo(session)

            user = ...

            if event.from_user.id in data.get('config').tg_bot.admin_ids:
                user = await repo.users.get_or_create_user(
                    event.from_user.id,
                    event.from_user.full_name,
                    event.from_user.username
                )
            else:
                user = await repo.users.get_user_by_id(event.from_user.id)

            if not user:
                # Пользователь не найден в базе данных
                await event.answer("У вас нет прав для использования этого бота.\n"
                                   "Отправьте сообщение ниже администратору:\n"
                                   '<a href="https://t.me/OxN1ck">https://t.me/OxN1ck</a>')
                await event.answer(f"<b>user_id:</b> {event.from_user.id}\n"
                                   f"<b>username:</b> {event.from_user.username}\n"
                                   f"<b>full_name:</b> {event.from_user.full_name}\n"
                                   f"<b>chat_id:</b> {event.chat.id}\n")
                return

            data["session"] = session
            data["repo"] = repo
            data["user"] = user

            result = await handler(event, data)
        return result
