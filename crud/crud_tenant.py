from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.tenant.model import Tenant
from backend.plugin.tenant.schema.tenant import CreateTenantParam, UpdateTenantParam


class CRUDTenant(CRUDPlus[Tenant]):
    async def get(self, db: AsyncSession, pk: int) -> Tenant | None:
        """
        获取租户

        :param db: 数据库会话
        :param pk: 租户 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_by_name(self, db: AsyncSession, name: str) -> Tenant | None:
        """
        通过名称获取租户

        :param db: 数据库会话
        :param name: 租户名称
        :return:
        """
        return await self.select_model_by_column(db, name=name)

    async def get_by_code(self, db: AsyncSession, code: str) -> Tenant | None:
        """
        通过编码获取租户

        :param db: 数据库会话
        :param code: 租户编码
        :return:
        """
        return await self.select_model_by_column(db, code=code)

    async def get_by_domain(self, db: AsyncSession, domain: str) -> Tenant | None:
        """
        通过域名获取租户

        :param db: 数据库会话
        :param domain: 租户域名
        :return:
        """
        return await self.select_model_by_column(db, domain=domain)

    async def get_select(
        self,
        *,
        name: str | None = None,
        code: str | None = None,
        domain: str | None = None,
        package_id: int | None = None,
        status: int | None = None,
    ) -> Select:
        """
        获取租户列表查询表达式

        :param name: 租户名称
        :param code: 租户编码
        :param domain: 租户域名
        :param package_id: 套餐 ID
        :param status: 状态
        :return:
        """
        filters = {}

        if name is not None:
            filters.update(name__like=f'%{name}%')
        if code is not None:
            filters.update(code=code)
        if domain is not None:
            filters.update(domain__like=f'%{domain}%')
        if package_id is not None:
            filters.update(package_id=package_id)
        if status is not None:
            filters.update(status=status)

        return await self.select_order('id', 'desc', **filters)

    async def get_all(self, db: AsyncSession) -> Sequence[Tenant]:
        """
        获取所有租户

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateTenantParam, code: str) -> Tenant:
        """
        创建租户

        :param db: 数据库会话
        :param obj: 创建租户参数
        :param code: 租户编码
        :return:
        """
        dict_obj = obj.model_dump(exclude={'admin_username', 'admin_password'})
        dict_obj.update({'code': code, 'admin_username': obj.admin_username})
        new_tenant = await self.create_model(db, dict_obj)
        await db.flush()
        return new_tenant

    async def update(self, db: AsyncSession, pk: int, obj: UpdateTenantParam) -> int:
        """
        更新租户

        :param db: 数据库会话
        :param pk: 租户 ID
        :param obj: 更新租户参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除租户

        :param db: 数据库会话
        :param pks: 租户 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_package_id(self, db: AsyncSession, package_id: int) -> Tenant | None:
        """
        通过套餐 ID 获取租户

        :param db: 数据库会话
        :param package_id: 套餐 ID
        :return:
        """
        return await self.select_model_by_column(db, package_id=package_id)

    async def get_ids_by_package_id(self, db: AsyncSession, package_id: int) -> list[int]:
        """
        通过套餐 ID 获取租户 ID 列表

        :param db: 数据库会话
        :param package_id: 套餐 ID
        :return:
        """
        tenants = await self.select_models(db, package_id=package_id)
        return [t.id for t in tenants]


tenant_dao: CRUDTenant = CRUDTenant(Tenant)
