from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class TenantPackageSchemaBase(SchemaBase):
    """租户套餐基础模型"""

    name: str = Field(description='套餐名称')
    sort: int = Field(default=999, description='排序')
    status: StatusType = Field(default=StatusType.enable, description='状态')
    remark: str | None = Field(None, description='备注')


class CreateTenantPackageParam(TenantPackageSchemaBase):
    """创建租户套餐参数"""

    menus: list[int] = Field(description='菜单 ID 列表')


class UpdateTenantPackageParam(SchemaBase):
    """更新租户套餐参数"""

    name: str | None = Field(None, description='套餐名称')
    sort: int | None = Field(None, description='排序')
    status: StatusType | None = Field(None, description='状态')
    menus: list[int] | None = Field(None, description='菜单 ID 列表')
    remark: str | None = Field(None, description='备注')


class GetTenantPackageDetail(TenantPackageSchemaBase):
    """租户套餐详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='套餐 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')

    menu_ids: list[int] = Field(default=[], description='关联的菜单 ID 列表')
