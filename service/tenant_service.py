from typing import Any

import bcrypt

from fast_captcha import text_captcha
from sqlalchemy import Select, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.model import Dept, Role, User
from backend.app.admin.model.login_log import LoginLog
from backend.app.admin.model.m2m import role_data_scope, role_menu, user_role
from backend.app.admin.model.opera_log import OperaLog
from backend.app.admin.model.user_password_history import UserPasswordHistory
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
    async def get_select(
        *,
        name: str | None = None,
        code: str | None = None,
        domain: str | None = None,
        package_id: int | None = None,
        status: int | None = None,
    ) -> Select:
        return await tenant_dao.get_select(
            name=name,
            code=code,
            domain=domain,
            package_id=package_id,
            status=status,
        )

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

        package = await tenant_package_dao.get(db, obj.package_id)
        if not package:
            raise errors.NotFoundError(msg='套餐不存在')
        if package.status == 0:
            raise errors.ForbiddenError(msg='租户套餐已被禁用')

        code = text_captcha(6)
        while await tenant_dao.get_by_code(db, code):
            code = text_captcha(6)

        tenant = await tenant_dao.create(db, obj, code)
        tenant_id = tenant.id

        dept = Dept(
            name=tenant.name,
            sort=0,
            status=1,
            del_flag=False,
            tenant_id=tenant_id,
        )
        db.add(dept)
        await db.flush()

        role = Role(
            name=settings.TENANT_ADMIN_DEFAULT_ROLE_NAME,
            status=1,
            is_filter_scopes=False,
            tenant_id=tenant_id,
        )
        db.add(role)
        await db.flush()

        menus = await tenant_package_dao.get_menus(db, tenant.package_id)
        if menus:
            menu_data = [{'role_id': role.id, 'menu_id': menu.id, 'tenant_id': tenant_id} for menu in menus]
            await db.execute(insert(role_menu), menu_data)

        salt = bcrypt.gensalt()
        hashed_password = get_hash_password(obj.admin_password, salt)
        admin_user = User(
            username=obj.admin_username,
            nickname=f'{tenant.name}管理员',
            password=hashed_password,
            salt=salt,
            status=1,
            is_superuser=False,
            is_staff=True,
            is_multi_login=False,
            dept_id=dept.id,
            tenant_id=tenant_id,
        )
        db.add(admin_user)
        await db.flush()

        await db.execute(
            insert(user_role),
            [{'user_id': admin_user.id, 'role_id': role.id, 'tenant_id': tenant_id}],
        )

        await db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(admin_user_id=admin_user.id, admin_username=obj.admin_username)
        )

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateTenantParam) -> int:  # noqa: C901
        tenant = await tenant_dao.get(db, pk)
        if not tenant:
            raise errors.NotFoundError(msg='租户不存在')

        if obj.name and obj.name != tenant.name:
            existing = await tenant_dao.get_by_name(db, obj.name)
            if existing:
                raise errors.ForbiddenError(msg='租户名称已存在')

        if obj.domain and obj.domain != tenant.domain:
            existing_domain = await tenant_dao.get_by_domain(db, obj.domain)
            if existing_domain:
                raise errors.ForbiddenError(msg='租户域名已存在')

        if obj.package_id and obj.package_id != tenant.package_id:
            package = await tenant_package_dao.get(db, obj.package_id)
            if not package:
                raise errors.NotFoundError(msg='套餐不存在')
            if package.status == 0:
                raise errors.ForbiddenError(msg='租户套餐已被禁用')

            stmt = select(Role).where(Role.tenant_id == pk, Role.name == settings.TENANT_ADMIN_DEFAULT_ROLE_NAME)
            admin_role = (await db.execute(stmt)).scalars().first()
            if admin_role:
                await db.execute(
                    delete(role_menu).where(role_menu.c.role_id == admin_role.id, role_menu.c.tenant_id == pk)
                )

                menus = await tenant_package_dao.get_menus(db, obj.package_id)
                if menus:
                    menu_data = [{'role_id': admin_role.id, 'menu_id': menu.id, 'tenant_id': pk} for menu in menus]
                    await db.execute(insert(role_menu), menu_data)

        return await tenant_dao.update(db, pk, obj)

    @staticmethod
    async def update_admin_password(*, db: AsyncSession, pk: int, password: str) -> None:
        tenant = await tenant_dao.get(db, pk)
        if not tenant:
            raise errors.NotFoundError(msg='租户不存在')
        if not tenant.admin_user_id:
            raise errors.NotFoundError(msg='租户管理员用户不存在')

        salt = bcrypt.gensalt()
        hashed_password = get_hash_password(password, salt)
        await db.execute(
            update(User).where(User.id == tenant.admin_user_id).values(password=hashed_password, salt=salt)
        )

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteTenantParam) -> int:
        for pk in obj.pks:
            tenant = await tenant_dao.get(db, pk)
            if not tenant:
                continue

            await db.execute(delete(user_role).where(user_role.c.tenant_id == pk))
            await db.execute(delete(role_menu).where(role_menu.c.tenant_id == pk))
            await db.execute(delete(role_data_scope).where(role_data_scope.c.tenant_id == pk))
            await db.execute(delete(UserPasswordHistory).where(UserPasswordHistory.tenant_id == pk))
            await db.execute(delete(OperaLog).where(OperaLog.tenant_id == pk))
            await db.execute(delete(LoginLog).where(LoginLog.tenant_id == pk))

            try:
                from backend.plugin.oauth2.model.user_social import UserSocial

                await db.execute(delete(UserSocial).where(UserSocial.tenant_id == pk))
            except ImportError:
                pass

            try:
                from backend.plugin.notice.model.notice import Notice

                await db.execute(delete(Notice).where(Notice.tenant_id == pk))
            except ImportError:
                pass

            await db.execute(delete(User).where(User.tenant_id == pk))
            await db.execute(delete(Role).where(Role.tenant_id == pk))
            await db.execute(delete(Dept).where(Dept.tenant_id == pk))

        return await tenant_dao.delete(db, obj.pks)


tenant_service: TenantService = TenantService()
