from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Numeric, create_engine, select

class Base(DeclarativeBase):
    pass

class Investment(Base):
    __tablename__ = 'investment'
    id: Mapped[int] = mapped_column(primary_key=True)
    coin: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    def __repr__(self) -> str:
        return f"<Investment coin: {self.coin}, currency: {self.currency}, amount: {self.amount}>"

engine = create_engine("sqlite:///manager.db")
Base.metadata.create_all(engine)

bitcoin = Investment(coin="bitcoin", currency="USD", amount=1000.00)
ethereum = Investment(coin="ethereum", currency="GBP", amount=100.00)
dogecoin = Investment(coin="dogecoin", currency="EUR", amount=500.00)

with Session(engine) as session:
    #session.add_all([bitcoin, ethereum, dogecoin])
    #session.commit()
    #stmt = select(Investment).where(Investment.coin == "bitcoin")
    #print(stmt)
    #result = session.execute(stmt).scalar_one()
    #print(result)
    # stmt = select(Investment).where(Investment.amount >= 5)
    # results = session.execute(stmt).scalars().all()
    # for investment in results:
    #     print(investment)
    # bitcoin = session.get(Investment, 1)
    # bitcoin.amount += 11
    # print(session.dirty)
    # dogecoin = session.get(Investment, 3)
    # session.delete(dogecoin)
    # session.commit()
    pass