-- Binary Manager v2 Database Schema
-- SQLite Database Schema

-- Publishers表：记录发布者信息
CREATE TABLE IF NOT EXISTS publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher_id TEXT NOT NULL UNIQUE,
    hostname TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_active_at TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Packages表：记录包信息（包含Git信息）
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL,
    version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- 发布者信息
    publisher_id TEXT NOT NULL,
    publisher_hostname TEXT NOT NULL,
    
    -- Git信息
    git_commit_hash TEXT NOT NULL,
    git_commit_short TEXT NOT NULL,
    git_branch TEXT,
    git_tag TEXT,
    git_author TEXT,
    git_author_email TEXT,
    git_commit_time TEXT,
    git_is_dirty INTEGER DEFAULT 0,
    
    -- 文件信息
    archive_name TEXT NOT NULL,
    archive_size INTEGER NOT NULL,
    archive_hash TEXT NOT NULL,
    file_count INTEGER NOT NULL,
    
    -- 存储信息
    storage_type TEXT NOT NULL DEFAULT 'local',
    storage_path TEXT NOT NULL,
    s3_bucket TEXT,
    s3_key TEXT,
    
    -- 元数据
    description TEXT,
    metadata TEXT,
    
    -- 约束
    UNIQUE(package_name, version, git_commit_hash)
);

-- Groups表：记录Group信息
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    description TEXT,
    environment_config TEXT,  -- JSON格式
    metadata TEXT,  -- JSON格式
    
    UNIQUE(group_name, version)
);

-- Group Packages表：Group和包的关联
CREATE TABLE IF NOT EXISTS group_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    package_id INTEGER NOT NULL,
    install_order INTEGER DEFAULT 0,
    required INTEGER DEFAULT 1,  -- 1=必需, 0=可选
    
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
    UNIQUE(group_id, package_id)
);

-- Dependencies表：依赖关系
CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    package_id INTEGER,
    depends_on_group_id INTEGER,
    depends_on_package_id INTEGER,
    constraint_type TEXT NOT NULL DEFAULT 'exact',  -- 'exact', 'minimum', 'range'
    version_constraint TEXT,
    
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_package_id) REFERENCES packages(id) ON DELETE CASCADE,
    
    CHECK (
        (package_id IS NOT NULL) OR 
        (depends_on_group_id IS NOT NULL) OR 
        (depends_on_package_id IS NOT NULL)
    )
);

-- Cache Status表：本地缓存状态
CREATE TABLE IF NOT EXISTS cache_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL UNIQUE,
    last_synced_at TEXT NOT NULL,
    last_sync_status TEXT NOT NULL DEFAULT 'pending',  -- 'success', 'failed', 'pending'
    record_count INTEGER NOT NULL DEFAULT 0,
    checksum TEXT NOT NULL DEFAULT '',
    error_message TEXT
);

-- Sync History表：同步历史
CREATE TABLE IF NOT EXISTS sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type TEXT NOT NULL,  -- 'upload', 'download'
    source TEXT NOT NULL,     -- 'local', 's3'
    target TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'success', 'failed', 'pending'
    record_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    checksum_before TEXT,
    checksum_after TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_packages_name_version ON packages(package_name, version);
CREATE INDEX IF NOT EXISTS idx_packages_git_commit ON packages(git_commit_hash);
CREATE INDEX IF NOT EXISTS idx_packages_publisher ON packages(publisher_id);
CREATE INDEX IF NOT EXISTS idx_groups_name_version ON groups(group_name, version);
CREATE INDEX IF NOT EXISTS idx_groups_created_by ON groups(created_by);
CREATE INDEX IF NOT EXISTS idx_group_packages_group ON group_packages(group_id);
CREATE INDEX IF NOT EXISTS idx_group_packages_package ON group_packages(package_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_group ON dependencies(group_id);
CREATE INDEX IF NOT EXISTS idx_sync_history_type ON sync_history(sync_type);
CREATE INDEX IF NOT EXISTS idx_sync_history_status ON sync_history(status);

-- 初始化触发器：更新时间戳
CREATE TRIGGER IF NOT EXISTS update_packages_timestamp
AFTER UPDATE ON packages
FOR EACH ROW
BEGIN
    UPDATE packages SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_groups_timestamp
AFTER UPDATE ON groups
FOR EACH ROW
BEGIN
    UPDATE groups SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_publishers_active
AFTER INSERT ON publishers
FOR EACH ROW
BEGIN
    UPDATE publishers SET last_active_at = datetime('now') WHERE id = NEW.id;
END;
