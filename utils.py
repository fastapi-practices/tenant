from collections.abc import Generator
from contextlib import contextmanager

from backend.common.context import ctx


@contextmanager
def tenant_context(tenant_id: int) -> Generator[None, None, None]:
    """
    在指定租户的上下文下执行操作

    租户隔离由全局监听器按当前租户过滤，跨租户操作需要显式切换上下文

    :param tenant_id: 租户 ID
    :return:
    """
    origin_tenant_id = ctx.tenant_id
    ctx.tenant_id = tenant_id
    try:
        yield
    finally:
        ctx.tenant_id = origin_tenant_id
