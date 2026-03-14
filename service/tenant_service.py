from typing import Any

import bcrypt

from fast_captcha import text_captcha
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.utils.password_security import get_hash_password
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.plugin.tenant.crud.crud_package import tenant_package_dao
from backend.plugin.tenant.crud.crud_tenant import tenant_dao
from backend.plugin.tenant.model import Tenant
from backend.plugin.tenant.schema.tenant import CreateTenantParam, DeleteTenantParam, UpdateTenantParam


class TenantService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> Tenant:
        tenant = await tenant_dao.get(db, pk)
        if not tenant:
            raise errors.NotFoundError(msg='租户不存在')
        return tenant

    @staticmethod
    async def get_by_code(*, db: AsyncSession, code: str) -> Tenant:
        tenant = await tenant_dao.get_by_code(db, code)
        if not tenant:
            raise errors.NotFoundError(msg='租户不存在')
        return tenant

    @staticmethod
    async def get_by_domain(*, db: AsyncSession, domain: str) -> Tenant | None:
        return await tenant_dao.get_by_domain(db, domain)

    @staticmethod
    async def get_id_by_domain(*, db: AsyncSession, domain: str) -> int | None:
        tenant = await tenant_dao.get_by_domain(db, domain)
        return tenant.id if tenant else None

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        name: str | None = None,
        code: str | None = None,
        domain: str | None = None,
        package_id: int | None = None,
        status: int | None = None,
    ) -> dict[str, Any]:
        tenant_select = await tenant_dao.get_select(
            name=name,
            code=code,
            domain=domain,
            package_id=package_id,
            status=status,
        )
        return await paging_data(db, tenant_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateTenantParam) -> None:
        existing = await tenant_dao.get_by_name(db, obj.name)
        if existing:
            raise errors.ForbiddenError(msg='租户名称已存在')

        if obj.domain:
            existing_domain = await tenant_dao.get_by_domain(db, obj.domain)
            if existing_domain:
                raise errors.ForbiddenError(msg='租户域名已存在')

        if len(obj.admin_password) < 6:
            raise errors.RequestError(msg='管理员密码长度不能少于6位')

        package = await tenant_package_dao.get(db, obj.package_id)
        if not package:
            raise errors.NotFoundError(msg='套餐不存在')
        if package.status == 0:
            raise errors.ForbiddenError(msg='租户套餐已被禁用')

        code = text_captcha(6)
        while await tenant_dao.get_by_code(db, code):
            code = text_captcha(6)

        tenant = await tenant_dao.create(db, obj, code)
        menu_ids = await tenant_package_dao.get_menu_ids(db, tenant.package_id)
        await tenant_dao.init_related_data(
            db,
            tenant=tenant,
            admin_username=obj.admin_username,
            admin_password=obj.admin_password,
            role_name=settings.TENANT_ADMIN_DEFAULT_ROLE_NAME,
            menu_ids=menu_ids,
        )

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateTenantParam) -> int:
        tenant = await tenant_dao.get(db, pk)
        if not tenant:
            raise errors.NotFoundError(msg='租户不存在')

        if obj.name != tenant.name:
            existing = await tenant_dao.get_by_name(db, obj.name)
            if existing:
                raise errors.ForbiddenError(msg='租户名称已存在')

        if obj.domain is not None and obj.domain != tenant.domain:
            existing_domain = await tenant_dao.get_by_domain(db, obj.domain)
            if existing_domain:
                raise errors.ForbiddenError(msg='租户域名已存在')

        if obj.package_id != tenant.package_id:
            package = await tenant_package_dao.get(db, obj.package_id)
            if not package:
                raise errors.NotFoundError(msg='套餐不存在')
            if package.status == 0:
                raise errors.ForbiddenError(msg='租户套餐已被禁用')

            menu_ids = await tenant_package_dao.get_menu_ids(db, obj.package_id)
            await tenant_dao.sync_admin_role_menus(
                db,
                tenant_id=pk,
                role_name=settings.TENANT_ADMIN_DEFAULT_ROLE_NAME,
                menu_ids=menu_ids,
            )

        return await tenant_dao.update(db, pk, obj)

    @staticmethod
    async def update_admin_password(*, db: AsyncSession, pk: int, password: str) -> None:
        if len(password) < 6:
            raise errors.RequestError(msg='密码长度不能少于6位')

        tenant = await tenant_dao.get(db, pk)
        if not tenant:
            raise errors.NotFoundError(msg='租户不存在')
        if not tenant.admin_user_id:
            raise errors.NotFoundError(msg='租户管理员用户不存在')

        await tenant_dao.update_admin_password(
            db, user_id=tenant.admin_user_id, password=password
        )

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteTenantParam) -> int:
        for pk in obj.pks:
            tenant = await tenant_dao.get(db, pk)
            if not tenant:
                continue

            await tenant_dao.delete_related_data(db, tenant_id=pk)

        return await tenant_dao.delete(db, obj.pks)


tenant_service: TenantService = TenantService()
