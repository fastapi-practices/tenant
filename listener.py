from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, Session

from backend.common.context import ctx
from backend.common.model import TenantMixin


def register_tenant_sqlalchemy_listeners() -> None:
    """注册租户相关的 SQLAlchemy 事件监听器"""

    @event.listens_for(Session, 'do_orm_execute', propagate=True)
    def _inject_tenant_filter(orm_execute_state: ORMExecuteState) -> None:
        if not orm_execute_state.is_select:
            return
        tenant_id = ctx.tenant_id
        if tenant_id is None:
            return
        mapper = orm_execute_state.bind_mapper
        if mapper and hasattr(mapper.entity, 'tenant_id'):
            orm_execute_state.statement = orm_execute_state.statement.where(mapper.entity.tenant_id == tenant_id)

    @event.listens_for(TenantMixin, 'before_insert', propagate=True)
    def _inject_tenant_id(mapper, connection, target) -> None:  # noqa: ANN001
        tenant_id = ctx.tenant_id
        if tenant_id is None:
            return
        if hasattr(target, 'tenant_id') and target.tenant_id is None:
            target.tenant_id = ctx.tenant_id
