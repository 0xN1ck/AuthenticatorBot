from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import Market
from infrastructure.database.repo.base import BaseRepo


class MarketRepo(BaseRepo):
    async def get_or_create_market(
        self,
        market_name: str,
        market_key: str
    ):
        """
        Creates or updates a new market in the database and returns the market object.
        :param market_id: The market's ID.
        :param market_name: The market's name.
        :param market_key: The market's key.
        :return: Market object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(Market)
            .values(
                market_name=market_name,
                market_key=market_key,
            )
            .on_conflict_do_update(
                index_elements=[Market.market_id],
                set_=dict(
                    market_name=market_name,
                    market_key=market_key,
                ),
            )
            .returning(Market)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_market_by_id(self, market_id: int):
        """
        Retrieves a market from the database based on the market_id.
        :param market_id: The market's ID.
        :return: Market object if found, None if not found or there was an error while making a transaction.
        """

        select_stmt = select(Market).where(Market.market_id == market_id)
        result = await self.session.execute(select_stmt)

        market = result.fetchone()

        # Возвращаем найденного рынка или None, если рынок не найден
        return market if market else None

    async def get_all_markets(self):
        """
        Retrieves all markets from the database.
        :return: List of Market objects, empty list if there are no markets or there was an error while making a transaction.
        """

        select_stmt = select(Market.market_name)
        result = await self.session.execute(select_stmt)

        markets = result.fetchall()

        # Возвращаем список всех рынков или пустой список, если рынки не найдены
        return markets if markets else []

    async def get_market_by_name(self, market_name: str):
        """
        Retrieves the market_key based on the market_name from the database.
        :param market_name: The market's name.
        :return: Market key if found, None if not found or there was an error while making a transaction.
        """
        select_stmt = select(Market).where(Market.market_name == market_name)
        result = await self.session.execute(select_stmt)

        market_key = result.scalar_one_or_none()

        # Возвращаем market_key, если найден, иначе None
        return market_key

    async def delete_market_by_name(self, market_name: str):
        """
        Deletes a market from the database based on the market_name.
        :param market_name: The market's name.
        :return: True if the market was successfully deleted, False otherwise.
        """
        delete_stmt = delete(Market).where(Market.market_name == market_name)
        result = await self.session.execute(delete_stmt)

        await self.session.commit()
        return result.rowcount > 0
