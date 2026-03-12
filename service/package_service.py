from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.plugin.tenant.crud.crud_package import tenant_package_dao
from backend.plugin.tenant.crud.crud_tenant import tenant_dao
from backend.plugin.tenant.model import TenantPackage
from backend.plugin.tenant.schema.package import (
    CreateTenantPackageParam,
    GetTenantPackageDetail,
    UpdateTenantPackageParam,
)
from backend.utils.build_tree import get_tree_data


class TenantPackageService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> dict[str, Any]:
        package = await tenant_package_dao.get(db, pk)
        if not package:
            raise errors.NotFoundError(msg='套餐不存在')
        menu_ids = await tenant_package_dao.get_menu_ids(db, pk)
        data = GetTenantPackageDetail.model_validate(package).model_dump()
        data['menu_ids'] = menu_ids
        return data

    @staticmethod
    async def get_menu_tree(*, db: AsyncSession, pk: int) -> list[dict[str, Any] | None]:
        package = await tenant_package_dao.get(db, pk)
        if not package:
            raise errors.NotFoundError(msg='套餐不存在')
        menus = await tenant_package_dao.get_menus(db, pk)
        return get_tree_data(menus) if menus else []

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        name: str | None = None,
        status: int | None = None,
    ) -> dict[str, Any]:
        package_select = await tenant_package_dao.get_select(name=name, status=status)
        return await paging_data(db, package_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> list[TenantPackage]:
        packages = await tenant_package_dao.get_all(db)
        return list(packages)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateTenantPackageParam) -> None:
        existing = await tenant_package_dao.get_by_name(db, obj.name)
        if existing:
            raise errors.ForbiddenError(msg='套餐名称已存在')

        package = await tenant_package_dao.create(db, obj)
        await tenant_package_dao.update_menus(db, package.id, obj.menus)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateTenantPackageParam) -> int:
        package = await tenant_package_dao.get(db, pk)
        if not package:
            raise errors.NotFoundError(msg='套餐不存在')

        if obj.name != package.name:
            existing = await tenant_package_dao.get_by_name(db, obj.name)
            if existing:
                raise errors.ForbiddenError(msg='套餐名称已存在')

        count = await tenant_package_dao.update(db, pk, obj)
        await tenant_package_dao.update_menus(db, pk, obj.menus)

        tenant_ids = await tenant_dao.get_ids_by_package_id(db, pk)
        for tenant_id in tenant_ids:
            await tenant_dao.sync_admin_role_menus(
                db,
                tenant_id=tenant_id,
                role_name=settings.TENANT_ADMIN_DEFAULT_ROLE_NAME,
                menu_ids=obj.menus,
            )

        return count or 1

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        tenant = await tenant_dao.get_by_package_id(db, pk)
        if tenant:
            raise errors.ForbiddenError(msg='存在关联此套餐的租户，不允许删除')

        await tenant_package_dao.delete_menus_by_package_id(db, pk)
        return await tenant_package_dao.delete(db, pk)


tenant_package_service: TenantPackageService = TenantPackageService()
