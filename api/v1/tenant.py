from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.core.conf import settings
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.tenant.schema.tenant import (
    CreateTenantParam,
    DeleteTenantParam,
    GetTenantDetail,
    UpdateTenantAdminPwdParam,
    UpdateTenantParam,
)
from backend.plugin.tenant.service.tenant_service import tenant_service

router = APIRouter()


@router.get('/enabled', summary='获取租户开启状态')
async def get_tenant_enabled_status() -> ResponseSchemaModel[bool]:
    return response_base.success(data=settings.TENANT_ENABLED)


@router.get('/id', summary='获取租户 ID')
async def get_tenant_id(
    db: CurrentSession,
    domain: Annotated[str, Query(description='租户域名')],
) -> ResponseSchemaModel[int | None]:
    tenant_id = await tenant_service.get_id_by_domain(db=db, domain=domain)
    return response_base.success(data=tenant_id)


@router.get('/{pk}', summary='获取租户详情', dependencies=[DependsJwtAuth])
async def get_tenant(
    db: CurrentSession, pk: Annotated[int, Path(description='租户 ID')]
) -> ResponseSchemaModel[GetTenantDetail]:
    tenant = await tenant_service.get(db=db, pk=pk)
    return response_base.success(data=tenant)


@router.get(
    '',
    summary='分页获取所有租户',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_tenants_paginated(
    db: CurrentSession,
    name: Annotated[str | None, Query(description='租户名称')] = None,
    code: Annotated[str | None, Query(description='租户编码')] = None,
    domain: Annotated[str | None, Query(description='租户域名')] = None,
    package_id: Annotated[int | None, Query(description='套餐 ID')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> ResponseSchemaModel[PageData[GetTenantDetail]]:
    page_data = await tenant_service.get_list(
        db=db,
        name=name,
        code=code,
        domain=domain,
        package_id=package_id,
        status=status,
    )
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建租户',
    dependencies=[
        Depends(RequestPermission('tenant:management:add')),
        DependsRBAC,
    ],
)
async def create_tenant(db: CurrentSessionTransaction, obj: CreateTenantParam) -> ResponseModel:
    await tenant_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新租户',
    dependencies=[
        Depends(RequestPermission('tenant:management:edit')),
        DependsRBAC,
    ],
)
async def update_tenant(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='租户 ID')], obj: UpdateTenantParam
) -> ResponseModel:
    count = await tenant_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/admin/password',
    summary='修改租户管理员密码',
    dependencies=[
        Depends(RequestPermission('tenant:management:pwd')),
        DependsRBAC,
    ],
)
async def update_tenant_admin_password(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='租户 ID')],
    obj: UpdateTenantAdminPwdParam,
) -> ResponseModel:
    await tenant_service.update_admin_password(db=db, pk=pk, password=obj.password)
    return response_base.success()


@router.delete(
    '',
    summary='批量删除租户',
    dependencies=[
        Depends(RequestPermission('tenant:management:del')),
        DependsRBAC,
    ],
)
async def delete_tenants(db: CurrentSessionTransaction, obj: DeleteTenantParam) -> ResponseModel:
    count = await tenant_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
