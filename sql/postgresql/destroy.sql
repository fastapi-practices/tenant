delete from sys_user_role where tenant_id > 0;
delete from sys_role_menu where tenant_id > 0;
delete from sys_user where tenant_id > 0;
delete from sys_role where tenant_id > 0;
delete from sys_dept where tenant_id > 0;

delete from sys_menu where name in ('AddTenant', 'EditTenant', 'DeleteTenant', 'ResetTenantAdminPwd', 'AddTenantPackage', 'EditTenantPackage', 'DeleteTenantPackage');
delete from sys_menu where name in ('TenantList', 'TenantPackage');
delete from sys_menu where name = 'TenantManagement';

drop table if exists sys_tenant_package_menu;
drop table if exists sys_tenant;
drop table if exists sys_tenant_package;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
