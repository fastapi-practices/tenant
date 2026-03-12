from collections.abc import Sequence

from sqlalchemy import Select, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import Dept, Role, User
from backend.app.admin.model.login_log import LoginLog
from backend.app.admin.model.m2m import role_data_scope, role_menu, user_role
from backend.app.admin.model.opera_log import OperaLog
from backend.app.admin.model.user_password_history import UserPasswordHistory
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
        new_tenant = self.model(**dict_obj)
        db.add(new_tenant)
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

    @staticmethod
    async def replace_role_menus(db: AsyncSession, *, role_id: int, tenant_id: int, menu_ids: list[int]) -> None:
        """
        重建角色菜单关联

        :param db: 数据库会话
        :param role_id: 角色 ID
        :param tenant_id: 租户 ID
        :param menu_ids: 菜单 ID 列表
        :return:
        """
        await db.execute(delete(role_menu).where(role_menu.c.role_id == role_id, role_menu.c.tenant_id == tenant_id))

        if menu_ids:
            await db.execute(
                insert(role_menu),
                [{'role_id': role_id, 'menu_id': menu_id, 'tenant_id': tenant_id} for menu_id in menu_ids],
            )

    @staticmethod
    async def sync_admin_role_menus(db: AsyncSession, *, tenant_id: int, role_name: str, menu_ids: list[int]) -> bool:
        """
        同步租户管理员角色菜单

        :param db: 数据库会话
        :param tenant_id: 租户 ID
        :param role_name: 角色名称
        :param menu_ids: 菜单 ID 列表
        :return:
        """
        stmt = select(Role).where(Role.tenant_id == tenant_id, Role.name == role_name)
        admin_role = (await db.execute(stmt)).scalars().first()
        if not admin_role:
            return False

        await CRUDTenant.replace_role_menus(db, role_id=admin_role.id, tenant_id=tenant_id, menu_ids=menu_ids)
        return True

    @staticmethod
    async def initialize_related_data(
        db: AsyncSession,
        *,
        tenant: Tenant,
        admin_username: str,
        hashed_password: str,
        salt: bytes,
        role_name: str,
        menu_ids: list[int],
    ) -> None:
        """
        初始化租户关联数据

        :param db: 数据库会话
        :param tenant: 租户对象
        :param admin_username: 管理员用户名
        :param hashed_password: 加密密码
        :param salt: 密码盐
        :param role_name: 管理员角色名称
        :param menu_ids: 菜单 ID 列表
        :return:
        """
        dept = Dept(
            name=tenant.name,
            sort=0,
            status=1,
            del_flag=False,
            tenant_id=tenant.id,
        )
        db.add(dept)
        await db.flush()

        role = Role(
            name=role_name,
            status=1,
            is_filter_scopes=False,
            tenant_id=tenant.id,
        )
        db.add(role)
        await db.flush()

        await CRUDTenant.replace_role_menus(db, role_id=role.id, tenant_id=tenant.id, menu_ids=menu_ids)

        admin_user = User(
            username=admin_username,
            nickname=f'{tenant.name}管理员',
            password=hashed_password,
            salt=salt,
            status=1,
            is_superuser=False,
            is_staff=True,
            is_multi_login=False,
            dept_id=dept.id,
            tenant_id=tenant.id,
        )
        db.add(admin_user)
        await db.flush()

        await db.execute(
            insert(user_role),
            [{'user_id': admin_user.id, 'role_id': role.id, 'tenant_id': tenant.id}],
        )

        await db.execute(
            update(Tenant)
            .where(Tenant.id == tenant.id)
            .values(admin_user_id=admin_user.id, admin_username=admin_username)
        )

    @staticmethod
    async def update_admin_password(db: AsyncSession, *, user_id: int, hashed_password: str, salt: bytes) -> None:
        """
        更新租户管理员密码

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hashed_password: 加密密码
        :param salt: 密码盐
        :return:
        """
        await db.execute(update(User).where(User.id == user_id).values(password=hashed_password, salt=salt))

    @staticmethod
    async def delete_related_data(db: AsyncSession, *, tenant_id: int) -> None:
        """
        删除租户关联数据

        :param db: 数据库会话
        :param tenant_id: 租户 ID
        :return:
        """
        await db.execute(delete(user_role).where(user_role.c.tenant_id == tenant_id))
        await db.execute(delete(role_menu).where(role_menu.c.tenant_id == tenant_id))
        await db.execute(delete(role_data_scope).where(role_data_scope.c.tenant_id == tenant_id))
        await db.execute(delete(UserPasswordHistory).where(UserPasswordHistory.tenant_id == tenant_id))
        await db.execute(delete(OperaLog).where(OperaLog.tenant_id == tenant_id))
        await db.execute(delete(LoginLog).where(LoginLog.tenant_id == tenant_id))

        try:
            from backend.plugin.oauth2.model.user_social import UserSocial

            user_stmt = select(User.id).where(User.tenant_id == tenant_id)
            user_result = await db.execute(user_stmt)
            user_ids = [row[0] for row in user_result.all()]
            if user_ids:
                await db.execute(delete(UserSocial).where(UserSocial.user_id.in_(user_ids)))
        except ImportError:
            pass

        try:
            from backend.plugin.notice.model.notice import Notice

            await db.execute(delete(Notice).where(Notice.tenant_id == tenant_id))
        except ImportError:
            pass

        await db.execute(delete(User).where(User.tenant_id == tenant_id))
        await db.execute(delete(Role).where(Role.tenant_id == tenant_id))
        await db.execute(delete(Dept).where(Dept.tenant_id == tenant_id))


tenant_dao: CRUDTenant = CRUDTenant(Tenant)
