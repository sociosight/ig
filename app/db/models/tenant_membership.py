from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TenantMembership(Base):
    __tablename__ = "tenant_memberships"

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.tenant_id"),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        primary_key=True,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="member",
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )