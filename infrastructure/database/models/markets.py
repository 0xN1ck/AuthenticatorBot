from sqlalchemy import String
from sqlalchemy import text, BIGINT, Boolean, true
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin, TableNameMixin


class Market(Base, TimestampMixin, TableNameMixin):
    """
    This class represents a Market in the application.

    Attributes:
        market_id (Mapped[int]): The unique identifier of the market.
        market_name (Mapped[str]): The name of the market.
        market_key (Mapped[str]): The secret key for the market.

    Methods:
        __repr__(): Returns a string representation of the Market object.

    Inherited Attributes:
        Inherits from Base, TimestampMixin, and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin, and TableNameMixin classes, which provide additional functionality.

    """
    market_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    market_name: Mapped[str] = mapped_column(String(128), unique=True)
    market_key: Mapped[str] = mapped_column(String(128))

    def __repr__(self):
        return f"<Market {self.market_id} {self.market_name}>"
