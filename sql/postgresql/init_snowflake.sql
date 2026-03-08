insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2139008052890697728, '租户管理', 'TenantManagement', '/tenant', 99, 'icon-park-outline:peoples', 0, null, null, 1, 1, 1, '', null, null, now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2139008052924252160, '租户管理', 'TenantList', '/tenant/list', 1, null, 1, '/tenant/list/index', null, 1, 1, 1, '', null, 2139008052890697728, now(), null),
(2139008052974583808, '套餐管理', 'TenantPackage', '/tenant/package', 2, null, 1, '/tenant/package/index', null, 1, 1, 1, '', null, 2139008052890697728, now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2139008053175910400, '新增', 'AddTenant', null, 1, null, 2, null, 'tenant:management:add', 1, 0, 1, '', null, 2139008052924252160, now(), null),
(2139008053238824960, '编辑', 'EditTenant', null, 2, null, 2, null, 'tenant:management:edit', 1, 0, 1, '', null, 2139008052924252160, now(), null),
(2139008053301739520, '删除', 'DeleteTenant', null, 3, null, 2, null, 'tenant:management:del', 1, 0, 1, '', null, 2139008052924252160, now(), null),
(2139008053364654080, '修改管理员密码', 'ResetTenantAdminPwd', null, 4, null, 2, null, 'tenant:management:pwd', 1, 0, 1, '', null, 2139008052924252160, now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2139008053507260416, '新增', 'AddTenantPackage', null, 1, null, 2, null, 'tenant:package:add', 1, 0, 1, '', null, 2139008052974583808, now(), null),
(2139008053570174976, '编辑', 'EditTenantPackage', null, 2, null, 2, null, 'tenant:package:edit', 1, 0, 1, '', null, 2139008052974583808, now(), null),
(2139008053637283840, '删除', 'DeleteTenantPackage', null, 3, null, 2, null, 'tenant:package:del', 1, 0, 1, '', null, 2139008052974583808, now(), null);
