from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from backend.common.context import ctx
from backend.common.model import TenantMixin


def register_tenant_sqlalchemy_listeners() -> None:
    """注册租户相关的 SQLAlchemy 事件监听器"""

    @event.listens_for(Session, 'do_orm_execute', propagate=True)
    def _inject_tenant_filter(orm_execute_state: ORMExecuteState) -> None:
        """为查询语句自动追加租户过滤条件"""
        if not orm_execute_state.is_select:
            return
        tenant_id = ctx.tenant_id
        orm_execute_state.statement = orm_execute_state.statement.options(
            with_loader_criteria(
                TenantMixin,
                lambda cls: cls.tenant_id == tenant_id,
                include_aliases=True,
            )
        )

    @event.listens_for(TenantMixin, 'before_insert', propagate=True)
    def _inject_tenant_id(mapper, connection, target) -> None:  # noqa: ANN001
        """为新增模型自动注入当前租户 ID"""
        if hasattr(target, 'tenant_id') and target.tenant_id is None:
            target.tenant_id = ctx.tenant_id
