from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, Relationship
from sqlalchemy import String, Numeric, create_engine, select, Text, ForeignKey

class Base(DeclarativeBase):
    pass

class Investment(Base):
    __tablename__ = 'investment'
    id: Mapped[int] = mapped_column(primary_key=True)
    coin: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey('portfolio.id'), nullable=False)
    portfolio: Mapped["Portfolio"] = Relationship(back_populates="investments")

    def __repr__(self) -> str:
        return f"<Investment coin: {self.coin}, currency: {self.currency}, amount: {self.amount}>"
    
class Portfolio(Base):
    __tablename__ = 'portfolio'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    investments: Mapped[list[Investment]] = Relationship(back_populates="portfolio")

    def __repr__(self) -> str:
        return f"<Portfolio name: {self.name}, description: {self.description} with {len(self.investments)} investments>"

engine = create_engine("sqlite:///manager.db")
Base.metadata.create_all(engine)

bitcoin = Investment(coin="bitcoin", currency="USD", amount=1000.00)
ethereum = Investment(coin="ethereum", currency="GBP", amount=100.00)
dogecoin = Investment(coin="dogecoin", currency="EUR", amount=500.00)
bitcoin_2 = Investment(coin="bitcoin", currency="EUR", amount=750.00)

portfolio_1 = Portfolio(name="Long-term Holdings", description="Cryptocurrency investments for long-term growth.")
portfolio_2 = Portfolio(name="Short-term Trades", description="Cryptocurrency investments for short-term trading.")
portfolio_3 = Portfolio(name="Altcoin Basket", description="A diversified portfolio of alternative cryptocurrencies.")

bitcoin.portfolio = portfolio_1
bitcoin_2.portfolio = portfolio_3
portfolio_2.investments = [ethereum, dogecoin]

with Session(engine) as session:
    #session.add(bitcoin)
    #session.add(portfolio_2)
    #session.add(portfolio_3)
    #session.commit()
    subq = select(Investment).where(Investment.coin == "bitcoin").subquery()
    stmt = select(Portfolio).join(subq, Portfolio.id == subq.c.portfolio_id)
    results = session.execute(stmt).scalars().all()
    print(results)