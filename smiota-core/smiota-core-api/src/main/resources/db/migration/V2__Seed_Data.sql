-- =============================================================================
-- V2__Seed_Data.sql
-- Seed Core RBAC Catalogs, Initial Roles, and Navigation Hierarchy (MySQL)
-- =============================================================================

-- 1. Insert Core Modules
INSERT IGNORE INTO modules (id, name, code, description, sort_order, active) VALUES
('10000000-0000-0000-0000-000000000001', 'System Management', 'SYSTEM', 'System configuration, monitoring and layout', 1, TRUE),
('10000000-0000-0000-0000-000000000002', 'Identity Management', 'IDENTITY', 'Users, credentials and profile management', 2, TRUE),
('10000000-0000-0000-0000-000000000003', 'Access Control', 'RBAC', 'Roles, permissions and resource entitlements', 3, TRUE),
('10000000-0000-0000-0000-000000000004', 'Master Lookups', 'LOOKUP', 'Lookup dictionaries and system master tables', 4, TRUE);

-- 2. Insert Security Resources
INSERT IGNORE INTO sec_resources (id, module_id, name, code, description, active) VALUES
('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'User Resource', 'USER', 'Management of system user accounts', TRUE),
('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', 'Role Resource', 'ROLE', 'Management of security roles', TRUE),
('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'Permission Resource', 'PERMISSION', 'Granular authorization permissions', TRUE),
('20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000001', 'Menu Resource', 'MENU', 'Navigation and menu item hierarchy', TRUE),
('20000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000004', 'Country Resource', 'COUNTRY', 'Country master lookup dataset', TRUE);

-- 3. Insert Security Permissions
INSERT IGNORE INTO sec_permissions (id, resource_id, name, code, action, description) VALUES
('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'Create Users', 'USER_CREATE', 'CREATE', 'Permission to create user accounts'),
('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', 'Read Users', 'USER_READ', 'READ', 'Permission to view user accounts'),
('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000001', 'Update Users', 'USER_UPDATE', 'UPDATE', 'Permission to update user accounts'),
('30000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000001', 'Delete Users', 'USER_DELETE', 'DELETE', 'Permission to delete user accounts'),

('30000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000002', 'Create Roles', 'ROLE_CREATE', 'CREATE', 'Permission to create security roles'),
('30000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000002', 'Read Roles', 'ROLE_READ', 'READ', 'Permission to view security roles'),
('30000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000002', 'Update Roles', 'ROLE_UPDATE', 'UPDATE', 'Permission to modify security roles'),
('30000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000002', 'Delete Roles', 'ROLE_DELETE', 'DELETE', 'Permission to remove security roles'),

('30000000-0000-0000-0000-000000000009', '20000000-0000-0000-0000-000000000003', 'Read Permissions', 'PERMISSION_READ', 'READ', 'Permission to list permissions'),

('30000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000004', 'Read Navigation Menu', 'MENU_READ', 'READ', 'Permission to view menu trees'),
('30000000-0000-0000-0000-000000000011', '20000000-0000-0000-0000-000000000004', 'Manage Navigation Menu', 'MENU_MANAGE', 'UPDATE', 'Permission to manage navigation menus'),

('30000000-0000-0000-0000-000000000012', '20000000-0000-0000-0000-000000000005', 'Create Countries', 'COUNTRY_CREATE', 'CREATE', 'Permission to create country entries'),
('30000000-0000-0000-0000-000000000013', '20000000-0000-0000-0000-000000000005', 'Read Countries', 'COUNTRY_READ', 'READ', 'Permission to view country master data'),
('30000000-0000-0000-0000-000000000014', '20000000-0000-0000-0000-000000000005', 'Update Countries', 'COUNTRY_UPDATE', 'UPDATE', 'Permission to update country master data'),
('30000000-0000-0000-0000-000000000015', '20000000-0000-0000-0000-000000000005', 'Delete Countries', 'COUNTRY_DELETE', 'DELETE', 'Permission to delete country master data');

-- 4. Insert Roles
INSERT IGNORE INTO sec_roles (id, name, code, description, is_system, active) VALUES
('40000000-0000-0000-0000-000000000001', 'Administrator', 'ROLE_ADMIN', 'Full system administration access', TRUE, TRUE),
('40000000-0000-0000-0000-000000000002', 'Standard User', 'ROLE_USER', 'Standard enterprise user access', TRUE, TRUE);

-- 5. Map Permissions to ROLE_ADMIN
INSERT IGNORE INTO sec_role_permissions (id, role_id, permission_id)
SELECT CONCAT('70000000-0000-0000-0000-', LPAD(ROW_NUMBER() OVER(), 12, '0')),
       '40000000-0000-0000-0000-000000000001',
       p.id
FROM sec_permissions p;

-- 6. Map Default Read Permissions to ROLE_USER
INSERT IGNORE INTO sec_role_permissions (id, role_id, permission_id)
SELECT CONCAT('80000000-0000-0000-0000-', LPAD(ROW_NUMBER() OVER(), 12, '0')),
       '40000000-0000-0000-0000-000000000002',
       p.id
FROM sec_permissions p
WHERE p.code IN ('MENU_READ', 'COUNTRY_READ');

-- 7. Insert Initial Navigation Hierarchy
-- Top-level SIDEBAR: Dashboard
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000001', NULL, 'Dashboard', 'dashboard', '/dashboard', NULL, 'SIDEBAR', 1, TRUE);

-- Top-level SIDEBAR: Administration (Parent folder)
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000002', NULL, 'Administration', 'admin_panel_settings', NULL, NULL, 'SIDEBAR', 2, TRUE);

-- Child SIDEBAR: Users under Administration
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000002', 'Users', 'people', '/admin/users', 'USER_READ', 'SIDEBAR', 1, TRUE);

-- Child SIDEBAR: Roles & Permissions under Administration
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000004', '50000000-0000-0000-0000-000000000002', 'Roles & RBAC', 'security', '/admin/rbac', 'ROLE_READ', 'SIDEBAR', 2, TRUE);

-- Child SIDEBAR: Countries Lookup under Administration
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000005', '50000000-0000-0000-0000-000000000002', 'Countries', 'flag', '/admin/countries', 'COUNTRY_READ', 'SIDEBAR', 3, TRUE);

-- Top-level PROFILE section: My Profile
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000006', NULL, 'My Profile', 'person', '/profile', NULL, 'PROFILE', 1, TRUE);

-- Top-level TOPBAR section: Notifications
INSERT IGNORE INTO sec_menu_items (id, parent_id, title, icon, path, permission_code, layout_section, sort_order, active) VALUES
('50000000-0000-0000-0000-000000000007', NULL, 'Notifications', 'notifications', '/notifications', NULL, 'TOPBAR', 1, TRUE);

-- 8. Sample Lookup Data: Countries
INSERT IGNORE INTO tbl_countries (id, code, name, description, active, sort_order) VALUES
('60000000-0000-0000-0000-000000000001', 'US', 'United States', 'United States of America', TRUE, 1),
('60000000-0000-0000-0000-000000000002', 'CA', 'Canada', 'Canada', TRUE, 2),
('60000000-0000-0000-0000-000000000003', 'GB', 'United Kingdom', 'United Kingdom of Great Britain and Northern Ireland', TRUE, 3),
('60000000-0000-0000-0000-000000000004', 'DE', 'Germany', 'Federal Republic of Germany', TRUE, 4),
('60000000-0000-0000-0000-000000000005', 'JP', 'Japan', 'Japan', TRUE, 5);
