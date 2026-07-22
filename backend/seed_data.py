import bcrypt
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Role, Asset


async def seed_users(session: AsyncSession):
    result = await session.execute(select(User).where(User.username == "admin"))
    if not result.scalars().first():
        users = [
            User(
                username="admin",
                email="admin@company.com",
                hashed_password=bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
                role="admin",
                is_active=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=90),
            ),
            User(
                username="manager_zhang",
                email="zhang@company.com",
                hashed_password=bcrypt.hashpw("manager123".encode(), bcrypt.gensalt()).decode(),
                role="manager",
                is_active=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=60),
            ),
            User(
                username="viewer_li",
                email="li@company.com",
                hashed_password=bcrypt.hashpw("viewer123".encode(), bcrypt.gensalt()).decode(),
                role="viewer",
                is_active=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
        ]
        session.add_all(users)
        await session.commit()


async def seed_roles(session: AsyncSession):
    result = await session.execute(select(Role).where(Role.name == "admin"))
    if not result.scalars().first():
        roles = [
            Role(name="admin", description="超级管理员", permissions='["user:create","user:delete","asset:*","audit:view"]'),
            Role(name="manager", description="部门经理", permissions='["asset:create","asset:update","audit:view"]'),
            Role(name="viewer", description="普通查看者", permissions='["asset:view","audit:view"]'),
        ]
        session.add_all(roles)
        await session.commit()


async def seed_assets(session: AsyncSession):
    result = await session.execute(select(Asset).limit(1))
    if not result.scalars().first():
        now = datetime.now(timezone.utc)
        assets = [
            Asset(name="Dell PowerEdge R740", category="server", department="IT部", owner_id=1, purchase_date=now - timedelta(days=500), status="active", value=85000, serial_number="SVC-PE-R740-001"),
            Asset(name="HP EliteDesk 800 G9", category="desktop", department="市场部", owner_id=2, purchase_date=now - timedelta(days=200), status="active", value=7500, serial_number="SN-EP-G9-042"),
            Asset(name="LG UltraWide 34寸", category="monitor", department="设计部", owner_id=3, purchase_date=now - timedelta(days=150), status="active", value=4200, serial_number="LM-UW-34-078"),
            Asset(name="Microsoft 365 E5", category="software", department="全公司", owner_id=1, purchase_date=now - timedelta(days=365), status="active", value=12000, serial_number="LIC-M365-E5-2026"),
            Asset(name="Cisco Catalyst 9300", category="network", department="IT部", owner_id=1, purchase_date=now - timedelta(days=400), status="active", value=45000, serial_number="SW-C9K-9300-003"),
            Asset(name="MacBook Pro M3 Max", category="desktop", department="开发部", owner_id=1, purchase_date=now - timedelta(days=90), status="maintenance", value=32000, serial_number="MBP-M3M-015"),
            Asset(name="Lenovo ThinkPad X1", category="laptop", department="销售一部", owner_id=2, purchase_date=now - timedelta(days=120), status="active", value=14000, serial_number="TP-X1C-089"),
            Asset(name="Epson 投影仪", category="peripheral", department="会议室A", owner_id=3, purchase_date=now - timedelta(days=60), status="active", value=28000, serial_number="PRJ-EBL8-012"),
            Asset(name="Synology DS923+", category="server", department="财务部", owner_id=1, purchase_date=now - timedelta(days=300), status="active", value=6800, serial_number="NAS-SY-D923-007"),
            Asset(name="Adobe Creative Cloud", category="software", department="设计部", owner_id=3, purchase_date=now - timedelta(days=250), status="active", value=18000, serial_number="LIC-ADBE-CC-2026"),
        ]
        session.add_all(assets)
        await session.commit()


async def seed_all(session: AsyncSession):
    await seed_roles(session)
    await seed_users(session)
    await seed_assets(session)