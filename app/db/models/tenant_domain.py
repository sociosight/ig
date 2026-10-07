from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TenantDomain(Base):
    __tablename__ = "tenant_domains"

    hostname: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.tenant_id"),
        index=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )