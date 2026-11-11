from fastapi import FastAPI

from backend.common.tenant import register_tenant_checker
from backend.plugin.tenant.listener import register_tenant_sqlalchemy_listeners
from backend.plugin.tenant.service.tenant_service import check_tenant_status


def setup(app: FastAPI) -> None:
    """
    注册租户能力

    租户插件负责提供租户状态校验与数据隔离，主框架只保留能力开关与上下文

    :param app: FastAPI 应用
    :return:
    """
    register_tenant_checker(check_tenant_status)
    register_tenant_sqlalchemy_listeners()
