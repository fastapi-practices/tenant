insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('租户管理', 'TenantManagement', '/tenant', 99, 'icon-park-outline:peoples', 0, null, null, 1, 1, 1, '', null, null, now(), null);

set @dir_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('租户管理', 'TenantList', '/tenant/list', 1, null, 1, '/tenant/list/index', null, 1, 1, 1, '', null, @dir_id, now(), null);

set @tenant_menu_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('套餐管理', 'TenantPackage', '/tenant/package', 2, null, 1, '/tenant/package/index', null, 1, 1, 1, '', null, @dir_id, now(), null);

set @package_menu_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增', 'AddTenant', null, 1, null, 2, null, 'tenant:management:add', 1, 0, 1, '', null, @tenant_menu_id, now(), null),
('编辑', 'EditTenant', null, 2, null, 2, null, 'tenant:management:edit', 1, 0, 1, '', null, @tenant_menu_id, now(), null),
('删除', 'DeleteTenant', null, 3, null, 2, null, 'tenant:management:del', 1, 0, 1, '', null, @tenant_menu_id, now(), null),
('修改管理员密码', 'ResetTenantAdminPwd', null, 4, null, 2, null, 'tenant:management:pwd', 1, 0, 1, '', null, @tenant_menu_id, now(), null);

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增', 'AddTenantPackage', null, 1, null, 2, null, 'tenant:package:add', 1, 0, 1, '', null, @package_menu_id, now(), null),
('编辑', 'EditTenantPackage', null, 2, null, 2, null, 'tenant:package:edit', 1, 0, 1, '', null, @package_menu_id, now(), null),
('删除', 'DeleteTenantPackage', null, 3, null, 2, null, 'tenant:package:del', 1, 0, 1, '', null, @package_menu_id, now(), null);
