"""
Seed Data Service
Initialize database with sample market data
"""
import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.market import MarketSnapshot


# Sample market data (matching frontend data)
SAMPLE_MARKET_DATA = [
    {
        "symbol": "PT",
        "name": "铂",
        "name_en": "Platinum",
        "exchange": "SHFE",
        "category": "metal",
        "latest_price": Decimal("268.15"),
        "price_change": Decimal("15.72"),
        "price_change_percent": Decimal("6.22"),
        "days_to_expiry": 75,
        "implied_vol": Decimal("66.24"),
        "iv_change": Decimal("11.49"),
        "iv_speed": Decimal("0.185"),
        "realized_vol": Decimal("95.74"),
        "premium": Decimal("-27.19"),
        "skew": Decimal("9.56"),
        "iv_percentile": 67,
        "skew_percentile": 34,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "PD",
        "name": "钯",
        "name_en": "Palladium",
        "exchange": "SHFE",
        "category": "metal",
        "latest_price": Decimal("457.95"),
        "price_change": Decimal("19.50"),
        "price_change_percent": Decimal("4.45"),
        "days_to_expiry": 75,
        "implied_vol": Decimal("62.66"),
        "iv_change": Decimal("-0.95"),
        "iv_speed": Decimal("-0.152"),
        "realized_vol": Decimal("85.62"),
        "premium": Decimal("-21.88"),
        "skew": Decimal("13.46"),
        "iv_percentile": 70,
        "skew_percentile": 85,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "510500",
        "name": "中证500ETF",
        "name_en": "CSI 500 ETF",
        "exchange": "SSE",
        "category": "index",
        "latest_price": Decimal("5.418"),
        "price_change": Decimal("0.087"),
        "price_change_percent": Decimal("1.64"),
        "days_to_expiry": 27,
        "implied_vol": Decimal("21.65"),
        "iv_change": Decimal("-1.19"),
        "iv_speed": Decimal("-0.029"),
        "realized_vol": Decimal("26.11"),
        "premium": Decimal("-3.84"),
        "skew": Decimal("-0.22"),
        "iv_percentile": 68,
        "skew_percentile": 43,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "510300",
        "name": "沪深300ETF",
        "name_en": "CSI 300 ETF",
        "exchange": "SSE",
        "category": "index",
        "latest_price": Decimal("4.042"),
        "price_change": Decimal("0.060"),
        "price_change_percent": Decimal("1.52"),
        "days_to_expiry": 27,
        "implied_vol": Decimal("15.23"),
        "iv_change": Decimal("-0.89"),
        "iv_speed": Decimal("-0.042"),
        "realized_vol": Decimal("18.45"),
        "premium": Decimal("-2.89"),
        "skew": Decimal("-0.35"),
        "iv_percentile": 42,
        "skew_percentile": 38,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "LC",
        "name": "碳酸锂",
        "name_en": "Lithium Carbonate",
        "exchange": "GFEX",
        "category": "new",
        "latest_price": Decimal("76980"),
        "price_change": Decimal("1042"),
        "price_change_percent": Decimal("1.37"),
        "days_to_expiry": 8,
        "implied_vol": Decimal("79.81"),
        "iv_change": Decimal("5.58"),
        "iv_speed": Decimal("2.651"),
        "realized_vol": Decimal("105.42"),
        "premium": Decimal("-25.61"),
        "skew": Decimal("-1.08"),
        "iv_percentile": 99,
        "skew_percentile": 5,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "SM",
        "name": "锰硅",
        "name_en": "Ferromanganese",
        "exchange": "ZCE",
        "category": "black",
        "latest_price": Decimal("7236"),
        "price_change": Decimal("185"),
        "price_change_percent": Decimal("2.62"),
        "days_to_expiry": 46,
        "implied_vol": Decimal("23.50"),
        "iv_change": Decimal("11.49"),
        "iv_speed": Decimal("0.956"),
        "realized_vol": Decimal("9.45"),
        "premium": Decimal("14.05"),
        "skew": Decimal("4.98"),
        "iv_percentile": 91,
        "skew_percentile": 97,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "CF",
        "name": "郑棉",
        "name_en": "Cotton",
        "exchange": "ZCE",
        "category": "agri",
        "latest_price": Decimal("13650"),
        "price_change": Decimal("140"),
        "price_change_percent": Decimal("1.04"),
        "days_to_expiry": 46,
        "implied_vol": Decimal("20.88"),
        "iv_change": Decimal("1.90"),
        "iv_speed": Decimal("0.245"),
        "realized_vol": Decimal("17.77"),
        "premium": Decimal("3.11"),
        "skew": Decimal("3.21"),
        "iv_percentile": 100,
        "skew_percentile": 97,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "SR",
        "name": "白糖",
        "name_en": "Sugar",
        "exchange": "ZCE",
        "category": "agri",
        "latest_price": Decimal("6088"),
        "price_change": Decimal("62"),
        "price_change_percent": Decimal("1.03"),
        "days_to_expiry": 46,
        "implied_vol": Decimal("9.74"),
        "iv_change": Decimal("-0.34"),
        "iv_speed": Decimal("-0.136"),
        "realized_vol": Decimal("9.43"),
        "premium": Decimal("0.31"),
        "skew": Decimal("0.74"),
        "iv_percentile": 60,
        "skew_percentile": 89,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "SN",
        "name": "沪锡",
        "name_en": "Tin",
        "exchange": "SHFE",
        "category": "metal",
        "latest_price": Decimal("268520"),
        "price_change": Decimal("2600"),
        "price_change_percent": Decimal("0.98"),
        "days_to_expiry": 27,
        "implied_vol": Decimal("58.41"),
        "iv_change": Decimal("4.00"),
        "iv_speed": Decimal("0.135"),
        "realized_vol": Decimal("73.46"),
        "premium": Decimal("-15.05"),
        "skew": Decimal("4.50"),
        "iv_percentile": 97,
        "skew_percentile": 87,
        "is_main": True,
        "is_foreign": False,
    },
    {
        "symbol": "FU",
        "name": "燃油",
        "name_en": "Fuel Oil",
        "exchange": "SHFE",
        "category": "energy",
        "latest_price": Decimal("2998"),
        "price_change": Decimal("57"),
        "price_change_percent": Decimal("1.94"),
        "days_to_expiry": 20,
        "implied_vol": Decimal("48.68"),
        "iv_change": Decimal("0.66"),
        "iv_speed": Decimal("0.391"),
        "realized_vol": Decimal("38.58"),
        "premium": Decimal("10.10"),
        "skew": Decimal("2.97"),
        "iv_percentile": 85,
        "skew_percentile": 70,
        "is_main": True,
        "is_foreign": False,
    },
]


async def seed_market_snapshots(db: AsyncSession):
    """Seed market snapshot data"""
    print("🌱 Seeding market snapshots...")
    
    for data in SAMPLE_MARKET_DATA:
        # Check if exists
        from sqlalchemy import select
        result = await db.execute(
            select(MarketSnapshot).where(MarketSnapshot.symbol == data["symbol"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            snapshot = MarketSnapshot(**data)
            db.add(snapshot)
    
    await db.commit()
    print(f"✅ Seeded {len(SAMPLE_MARKET_DATA)} market snapshots")


async def seed_all_data():
    """Seed all initial data"""
    async with AsyncSessionLocal() as db:
        await seed_market_snapshots(db)


if __name__ == "__main__":
    asyncio.run(seed_all_data())
