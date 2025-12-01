from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

class Base(DeclarativeBase):
    pass

class Investment(Base):
    __tablename__ = 'investment'
    id: Mapped[int] = mapped_column(primary_key=True)
    coin: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)