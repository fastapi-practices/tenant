from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.admin.schema.menu import GetMenuTree
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.tenant.crud.crud_package import tenant_package_dao
from backend.plugin.tenant.schema.package import (
    CreateTenantPackageParam,
    GetTenantPackageDetail,
    UpdateTenantPackageParam,
)
from backend.plugin.tenant.service.package_service import tenant_package_service

router = APIRouter()


@router.get('/{pk}', summary='获取套餐详情', dependencies=[DependsJwtAuth])
async def get_tenant_package(
    db: CurrentSession, pk: Annotated[int, Path(description='套餐 ID')]
) -> ResponseSchemaModel[GetTenantPackageDetail]:
    package = await tenant_package_service.get(db=db, pk=pk)
    return response_base.success(data=package)


@router.get('/{pk}/menus', summary='获取套餐菜单树', dependencies=[DependsJwtAuth])
async def get_tenant_package_menus(
    db: CurrentSession, pk: Annotated[int, Path(description='套餐 ID')]
) -> ResponseSchemaModel[list[GetMenuTree] | None]:
    menus = await tenant_package_service.get_menu_tree(db=db, pk=pk)
    return response_base.success(data=menus)


@router.get(
    '',
    summary='分页获取所有套餐',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_tenant_packages_paginated(
    db: CurrentSession,
    name: Annotated[str | None, Query(description='套餐名称')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> ResponseSchemaModel[PageData[GetTenantPackageDetail]]:
    package_select = await tenant_package_dao.get_select(name=name, status=status)
    page_data = await paging_data(db, package_select)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建套餐',
    dependencies=[
        Depends(RequestPermission('tenant:package:add')),
        DependsRBAC,
    ],
)
async def create_tenant_package(db: CurrentSessionTransaction, obj: CreateTenantPackageParam) -> ResponseModel:
    await tenant_package_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新套餐',
    dependencies=[
        Depends(RequestPermission('tenant:package:edit')),
        DependsRBAC,
    ],
)
async def update_tenant_package(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='套餐 ID')], obj: UpdateTenantPackageParam
) -> ResponseModel:
    count = await tenant_package_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除套餐',
    dependencies=[
        Depends(RequestPermission('tenant:package:del')),
        DependsRBAC,
    ],
)
async def delete_tenant_package(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='套餐 ID')]
) -> ResponseModel:
    count = await tenant_package_service.delete(db=db, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
