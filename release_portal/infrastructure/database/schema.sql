-- Release Portal Database Schema
-- Extension of Binary Manager V2 database

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    role_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id TEXT NOT NULL,
    permission TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    PRIMARY KEY (role_id, permission, resource_type),
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
);

-- 许可证表
CREATE TABLE IF NOT EXISTS licenses (
    license_id TEXT PRIMARY KEY,
    organization TEXT NOT NULL,
    access_level TEXT NOT NULL,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- 许可证资源类型关联表
CREATE TABLE IF NOT EXISTS license_resource_types (
    license_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    PRIMARY KEY (license_id, resource_type),
    FOREIGN KEY (license_id) REFERENCES licenses(license_id) ON DELETE CASCADE
);

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id TEXT NOT NULL,
    license_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (license_id) REFERENCES licenses(license_id)
);

-- 发布记录表
CREATE TABLE IF NOT EXISTS releases (
    release_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    version TEXT NOT NULL,
    publisher_id TEXT NOT NULL,
    description TEXT,
    changelog TEXT,
    source_package_id TEXT,
    binary_package_id TEXT,
    doc_package_id TEXT,
    status TEXT DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES users(user_id),
    FOREIGN KEY (source_package_id) REFERENCES packages(id) ON DELETE SET NULL,
    FOREIGN KEY (binary_package_id) REFERENCES packages(id) ON DELETE SET NULL,
    FOREIGN KEY (doc_package_id) REFERENCES packages(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_licenses_organization ON licenses(organization);
CREATE INDEX IF NOT EXISTS idx_releases_resource_type ON releases(resource_type);
CREATE INDEX IF NOT EXISTS idx_releases_version ON releases(resource_type, version);
CREATE INDEX IF NOT EXISTS idx_releases_status ON releases(status);
CREATE INDEX IF NOT EXISTS idx_releases_publisher_id ON releases(publisher_id);
