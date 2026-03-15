from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class TenantSchemaBase(SchemaBase):
    """租户基础模型"""

    package_id: int = Field(description='套餐 ID')
    name: str = Field(description='租户名称')
    contact: str | None = Field(None, description='联系人')
    phone: str | None = Field(None, description='手机号')
    domain: str | None = Field(None, description='租户域名')
    expire_time: datetime | None = Field(None, description='过期时间')
    status: StatusType = Field(default=StatusType.enable, description='状态')
    remark: str | None = Field(None, description='备注')


class CreateTenantParam(TenantSchemaBase):
    """创建租户参数"""

    admin_username: str = Field(description='管理员用户名')
    admin_password: str = Field(description='管理员密码')


class UpdateTenantParam(TenantSchemaBase):
    """更新租户参数"""


class UpdateTenantAdminPwdParam(SchemaBase):
    """修改租户管理员密码参数"""

    password: str = Field(description='新密码')


class DeleteTenantParam(SchemaBase):
    """批量删除租户参数"""

    pks: list[int] = Field(description='租户 ID 列表')


class GetTenantDetail(TenantSchemaBase):
    """租户详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='租户 ID')
    code: str = Field(description='租户编码')
    admin_user_id: int | None = Field(None, description='管理员用户 ID')
    admin_username: str | None = Field(None, description='管理员用户名')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')
