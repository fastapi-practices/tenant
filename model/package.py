import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class TenantPackage(Base):
    """租户套餐表"""

    __tablename__ = 'sys_tenant_package'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), unique=True, index=True, comment='套餐名称')
    sort: Mapped[int] = mapped_column(default=999, comment='排序')
    status: Mapped[int] = mapped_column(default=1, comment='状态（0停用 1正常）')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='备注')
