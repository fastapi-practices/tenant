from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, UniversalText, id_key


class Tenant(Base):
    """租户表"""

    __tablename__ = 'sys_tenant'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), unique=True, index=True, comment='租户名称')
    code: Mapped[str] = mapped_column(sa.String(64), unique=True, index=True, comment='租户编码')
    package_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='套餐 ID')
    admin_user_id: Mapped[int | None] = mapped_column(sa.BigInteger, init=False, default=None, comment='管理员用户 ID')
    admin_username: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='管理员用户名')
    contact: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='联系人')
    phone: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='手机号')
    domain: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='租户域名')
    expire_time: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='过期时间')
    status: Mapped[int] = mapped_column(default=1, comment='状态（0停用 1正常）')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='备注')
