from typing import Any

from backend.common.context import ctx


def get_tenant_dict(obj: dict[str, Any]) -> dict[str, Any]:
    """
    向数据字典中注入 tenant_id

    :param obj: 数据字典
    :return:
    """
    if 'tenant_id' not in obj:
        obj['tenant_id'] = ctx.tenant_id
    return obj
