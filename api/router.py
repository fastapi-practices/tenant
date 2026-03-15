from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.tenant.api.v1.package import router as package_router
from backend.plugin.tenant.api.v1.tenant import router as tenant_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(tenant_router, prefix='/tenants', tags=['租户管理'])
v1.include_router(package_router, prefix='/tenant/packages', tags=['租户套餐管理'])
