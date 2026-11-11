# 多租户

为系统提供多租户能力，包括租户管理、套餐管理和租户数据隔离辅助能力

- 支持租户和套餐管理
- 支持创建租户管理员和初始化租户关联数据
- 提供 SQLAlchemy 监听器用于租户数据隔离扩展

## 插件类型

- 应用级插件

## 配置说明

插件目录下 `plugin.toml` 的 `[settings]` 中包含以下内容：

```toml
[settings]
TENANT_ADMIN_DEFAULT_ROLE_NAME = "租户管理员"
TENANT_DEFAULT_ID = 0
TENANT_ENABLED = false  # 是否启用多租户能力
```

在 `backend/core/conf.py` 中添加以下内容：

```python
##################################################
# [ Plugin ] tenant
##################################################
# 基础配置（in plugin.toml）
TENANT_ADMIN_DEFAULT_ROLE_NAME: str = '租户管理员'
TENANT_DEFAULT_ID: int = 0
TENANT_ENABLED: bool = False  # 租户是可选能力，开启后需要安装 tenant 插件
```

## 配置项说明

- `TENANT_ADMIN_DEFAULT_ROLE_NAME`：控制新建租户时初始化的管理员角色名称
- `TENANT_DEFAULT_ID`：控制默认租户的 ID
- `TENANT_ENABLED`：控制是否启用多租户数据隔离能力

## 使用方式

1. 安装并启用插件，把 `TENANT_ENABLED` 设为 `true` 后重启后端服务
2. 检查涉及租户的业务表，确保租户 ID 列存在，旧表需要手动迁移
3. 创建租户套餐并配置菜单权限
4. 创建租户时填写管理员账号和密码，系统会初始化租户部门、角色、用户及权限数据

## 卸载说明

- 卸载插件后，建议同步移除相关配置
- 如业务流程已依赖租户隔离能力，请同步清理对应集成

## 联系方式

- 作者：`wu-clan`
- 反馈方式：提交 Issue 或 PR
