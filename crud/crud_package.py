from collections.abc import Sequence

from sqlalchemy import Select, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import Menu
from backend.plugin.tenant.model import TenantPackage
from backend.plugin.tenant.model.m2m import package_menu
from backend.plugin.tenant.schema.package import CreateTenantPackageParam, UpdateTenantPackageParam


class CRUDTenantPackage(CRUDPlus[TenantPackage]):
    async def get(self, db: AsyncSession, pk: int) -> TenantPackage | None:
        """
        获取套餐

        :param db: 数据库会话
        :param pk: 套餐 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_by_name(self, db: AsyncSession, name: str) -> TenantPackage | None:
        """
        通过名称获取套餐

        :param db: 数据库会话
        :param name: 套餐名称
        :return:
        """
        return await self.select_model_by_column(db, name=name)

    async def get_select(
        self,
        *,
        name: str | None = None,
        status: int | None = None,
    ) -> Select:
        """
        获取套餐列表查询表达式

        :param name: 套餐名称
        :param status: 状态
        :return:
        """
        filters = {}

        if name is not None:
            filters.update(name__like=f'%{name}%')
        if status is not None:
            filters.update(status=status)

        return await self.select_order('sort', 'asc', **filters)

    async def get_all(self, db: AsyncSession) -> Sequence[TenantPackage]:
        """
        获取所有套餐

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateTenantPackageParam) -> TenantPackage:
        """
        创建套餐

        :param db: 数据库会话
        :param obj: 创建套餐参数
        :return:
        """
        dict_obj = obj.model_dump(exclude={'menus'})
        new_package = await self.create_model(db, dict_obj)
        await db.flush()
        return new_package

    async def update(self, db: AsyncSession, pk: int, obj: UpdateTenantPackageParam) -> int:
        """
        更新套餐

        :param db: 数据库会话
        :param pk: 套餐 ID
        :param obj: 更新套餐参数
        :return:
        """
        dict_obj = obj.model_dump(exclude={'menus'}, exclude_none=True)
        return await self.update_model(db, pk, dict_obj)

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """
        删除套餐

        :param db: 数据库会话
        :param pk: 套餐 ID
        :return:
        """
        return await self.delete_model(db, pk)

    @staticmethod
    async def get_menu_ids(db: AsyncSession, package_id: int) -> list[int]:
        """
        获取套餐关联的菜单 ID 列表

        :param db: 数据库会话
        :param package_id: 套餐 ID
        :return:
        """
        stmt = select(package_menu.c.menu_id).where(package_menu.c.package_id == package_id)
        result = await db.execute(stmt)
        return [row[0] for row in result.all()]

    @staticmethod
    async def get_menus(db: AsyncSession, package_id: int) -> Sequence[Menu] | None:
        """
        获取套餐菜单

        :param db: 数据库会话
        :param package_id: 套餐 ID
        :return:
        """
        stmt = (
            select(Menu)
            .join(package_menu, Menu.id == package_menu.c.menu_id)
            .where(package_menu.c.package_id == package_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_menus(db: AsyncSession, package_id: int, menu_ids: list[int]) -> None:
        """
        更新套餐菜单关联

        :param db: 数据库会话
        :param package_id: 套餐 ID
        :param menu_ids: 菜单 ID 列表
        :return:
        """
        # 删除旧关联
        del_stmt = delete(package_menu).where(package_menu.c.package_id == package_id)
        await db.execute(del_stmt)

        # 添加新关联
        if menu_ids:
            ins_stmt = insert(package_menu)
            await db.execute(
                ins_stmt,
                [{'package_id': package_id, 'menu_id': menu_id} for menu_id in menu_ids],
            )

    @staticmethod
    async def delete_menus_by_package_id(db: AsyncSession, package_id: int) -> None:
        """
        通过套餐 ID 删除菜单关联

        :param db: 数据库会话
        :param package_id: 套餐 ID
        :return:
        """
        del_stmt = delete(package_menu).where(package_menu.c.package_id == package_id)
        await db.execute(del_stmt)


tenant_package_dao: CRUDTenantPackage = CRUDTenantPackage(TenantPackage)
