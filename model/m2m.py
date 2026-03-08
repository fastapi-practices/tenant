import sqlalchemy as sa

from backend.common.model import MappedBase

# 套餐菜单关联表
package_menu = sa.Table(
    'sys_tenant_package_menu',
    MappedBase.metadata,
    sa.Column('id', sa.BigInteger, primary_key=True, unique=True, index=True, autoincrement=True, comment='主键 ID'),
    sa.Column('package_id', sa.BigInteger, nullable=False, index=True, comment='套餐 ID'),
    sa.Column('menu_id', sa.BigInteger, nullable=False, index=True, comment='菜单 ID'),
)
