from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(
        self,
        user_id: int,
        full_name: str,
        username: Optional[str] = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                full_name=full_name,
            )
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                    full_name=full_name,
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user from the database based on the user_id.
        :param user_id: The user's ID.
        :return: User object if found, None if not found or there was an error while making a transaction.
        """

        select_stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(select_stmt)

        user = result.fetchone()

        # Возвращаем найденного пользователя или None, если пользователь не найден
        return user if user else None

    async def get_all_users(self):
        """
        Retrieves all users from the database.
        :return: List of User objects or an empty list if there are no users or an error occurred.
        """
        select_stmt = select(User)
        result = await self.session.execute(select_stmt)

        users = result.fetchall()

        # Возвращаем список пользователей или пустой список, если пользователи не найдены
        return users if users else []

    async def delete_user_by_id(self, user_id: int):
        """
        Deletes a user from the database based on the user_id.
        :param user_id: The user's ID.
        :return: True if the user was successfully deleted, False if not found or there was an error.
        """
        delete_stmt = delete(User).where(User.user_id == user_id)
        result = await self.session.execute(delete_stmt)

        await self.session.commit()
        return result.rowcount > 0  # rowcount will be greater than 0 if the user was deleted
