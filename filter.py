from backend.common.context import ctx


def get_tenant_dict(obj: dict) -> dict:
    """
    向数据字典中注入 tenant_id

    :param obj: 数据字典
    :return:
    """
    tenant_id = ctx.tenant_id
    if tenant_id is not None and 'tenant_id' not in obj:
        obj['tenant_id'] = tenant_id
    return obj
