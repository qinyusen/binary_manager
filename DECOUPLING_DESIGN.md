# 账号系统与存储系统解耦设计

## 概述

本文档描述了地瓜机器人发布平台 V3 中账号系统和存储系统的解耦设计。

## 解耦目标

1. **账号系统**：管理用户、角色、许可证，独立于存储系统运行
2. **存储系统**：管理包的存储和下载，独立于账号系统运行
3. **解耦接口**：通过接口层连接两个系统，实现松耦合

## 架构设计

### 1. 核心接口

#### IAuthorizationService（授权服务接口）

位于 `release_portal/domain/services/i_authorization_service.py`

**职责**：
- 定义权限验证的接口契约
- 不依赖具体实现
- 可以有不同的实现（例如基于数据库、基于LDAP等）

**主要方法**：
```python
def can_download_release(user_id: str, resource_type: ResourceType) -> bool:
    """验证用户是否可以下载指定类型的资源"""

def can_download_content(user_id: str, resource_type: ResourceType, content_type: ContentType) -> bool:
    """验证用户是否可以下载指定内容类型"""

def can_publish(user_id: str, resource_type: ResourceType) -> bool:
    """验证用户是否可以发布指定类型的资源"""

def get_user_license_info(user_id: str) -> Optional[dict]:
    """获取用户的许可证信息"""

def validate_user_license(user_id: str) -> bool:
    """验证用户的许可证是否有效"""
```

#### IStorageService（存储服务接口）

位于 `release_portal/domain/services/i_storage_service.py`

**职责**：
- 定义存储操作的接口契约
- 不依赖具体实现
- 可以适配不同的存储后端（Binary Manager V2、S3、本地文件系统等）

**主要方法**：
```python
def publish_package(source_dir: str, package_name: str, version: str, extract_git: bool = True) -> dict:
    """发布包到存储系统"""

def download_package(package_id: Union[str, int], output_dir: str) -> None:
    """从存储系统下载包"""

def get_package_info(package_id: Union[str, int]) -> dict:
    """获取包信息"""
```

### 2. 实现类

#### AuthorizationService

位于 `release_portal/application/authorization_service.py`

**依赖**：
- UserRepository（账号系统）
- LicenseRepository（账号系统）

**特点**：
- 纯粹的账号系统逻辑
- 不依赖任何存储系统组件
- 可以独立测试和运行

#### StorageServiceAdapter

位于 `release_portal/application/storage_service_adapter.py`

**依赖**：
- PublisherService（Binary Manager V2 存储系统）
- DownloaderService（Binary Manager V2 存储系统）
- PackageRepository（Binary Manager V2 存储系统）

**特点**：
- 适配器模式，将 Binary Manager V2 的服务适配到 IStorageService 接口
- 纯粹的存储系统逻辑
- 不依赖任何账号系统组件

### 3. 业务服务

#### DownloadService

位于 `release_portal/application/download_service.py`

**依赖**：
- IAuthorizationService（接口）
- IStorageService（接口）
- UserRepository（账号系统）
- ReleaseRepository（发布系统）

**职责**：
- 协调授权和存储操作
- 通过接口调用，不直接依赖具体实现
- 可以轻松替换授权服务或存储服务的实现

#### ReleaseService

位于 `release_portal/application/release_service.py`

**依赖**：
- IStorageService（接口）
- ReleaseRepository（发布系统）
- IAuthorizationService（可选，接口）

**职责**：
- 管理发布流程
- 通过接口调用存储服务
- 可选的权限验证（通过授权服务）

## 解耦的优势

### 1. 独立开发
- 账号系统可以独立开发和测试
- 存储系统可以独立开发和测试
- 两个系统可以并行开发，互不影响

### 2. 灵活替换
- 可以轻松替换存储系统实现（例如从 Binary Manager V2 切换到 S3）
- 可以轻松替换授权系统实现（例如从数据库切换到 LDAP）
- 只需实现接口，业务逻辑无需修改

### 3. 易于测试
- 可以为接口创建 Mock 实现，方便单元测试
- 测试账号系统时不需要启动存储系统
- 测试存储系统时不需要启动账号系统

### 4. 可扩展性
- 可以添加多个存储系统实现（例如 S3StorageService、LocalStorageService）
- 可以添加多个授权系统实现（例如 LDAPAuthorizationService、OAuthAuthorizationService）
- 通过依赖注入，可以灵活配置使用哪个实现

## 使用示例

### 创建服务容器

```python
from release_portal.initializer import create_container

# 创建容器，自动组装所有服务
container = create_container("./data/portal.db")

# 获取服务
auth_service = container.auth_service
authorization_service = container.authorization_service
release_service = container.release_service
download_service = container.download_service
license_service = container.license_service
```

### 使用授权服务

```python
# 验证用户权限
can_publish = authorization_service.can_publish(user_id, ResourceType.BSP)
can_download = authorization_service.can_download_release(user_id, ResourceType.BSP)

# 获取用户许可证信息
license_info = authorization_service.get_user_license_info(user_id)
```

### 使用存储服务

```python
# 发布包
result = storage_service.publish_package(
    source_dir="/path/to/source",
    package_name="bsp-diggo-1-0-0-binary",
    version="1.0.0",
    extract_git=False
)
package_id = result['package_id']

# 下载包
storage_service.download_package(package_id, "/path/to/output")

# 获取包信息
package_info = storage_service.get_package_info(package_id)
```

### 使用下载服务（协调两个系统）

```python
# 获取用户可下载的包
packages = download_service.get_available_packages(user_id, release_id)

# 下载包
download_service.download_package(user_id, release_id, "BINARY", "/path/to/output")
```

## 文件结构

```
release_portal/
├── domain/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── i_authorization_service.py    # 授权服务接口
│   │   └── i_storage_service.py          # 存储服务接口
│   ├── entities/
│   │   ├── user.py                       # 用户实体（账号系统）
│   │   ├── role.py                       # 角色实体（账号系统）
│   │   ├── license.py                    # 许可证实体（账号系统）
│   │   └── release.py                    # 发布实体（发布系统）
│   └── repositories/
│       ├── user_repository.py            # 用户仓储（账号系统）
│       ├── license_repository.py         # 许可证仓储（账号系统）
│       └── release_repository.py         # 发布仓储（发布系统）
├── application/
│   ├── auth_service.py                   # 认证服务（账号系统）
│   ├── authorization_service.py          # 授权服务实现（账号系统）
│   ├── license_service.py                # 许可证服务（账号系统）
│   ├── storage_service_adapter.py        # 存储服务适配器（存储系统）
│   ├── release_service.py                # 发布服务（业务服务）
│   └── download_service.py               # 下载服务（业务服务）
└── infrastructure/
    ├── database/
    │   ├── sqlite_user_repository.py     # SQLite 用户仓储
    │   ├── sqlite_license_repository.py  # SQLite 许可证仓储
    │   └── sqlite_release_repository.py  # SQLite 发布仓储
    └── auth/
        └── token_service.py              # Token 服务（账号系统）

binary_manager_v2/                         # 独立的存储系统
├── application/
│   ├── publisher_service.py              # 发布服务
│   └── downloader_service.py             # 下载服务
└── infrastructure/
    └── database/
        └── sqlite_package_repository.py  # 包仓储
```

## 依赖注入

所有服务通过 `create_container()` 函数进行依赖注入：

```python
def create_container(db_path: str = None):
    # 创建仓储（账号系统）
    role_repo = SQLiteRoleRepository(db_path)
    user_repo = SQLiteUserRepository(db_path, role_repo)
    license_repo = SQLiteLicenseRepository(db_path)
    
    # 创建存储系统（Binary Manager V2）
    package_repo = SQLitePackageRepository(db_path)
    publisher_service = PublisherService(package_repository=package_repo)
    downloader_service = DownloaderService(package_repository=package_repo)
    
    # 创建授权服务（账号系统）
    authorization_service = AuthorizationService(
        user_repository=user_repo,
        license_repository=license_repo
    )
    
    # 创建存储适配器（适配 Binary Manager V2）
    storage_service = StorageServiceAdapter(
        publisher_service=publisher_service,
        downloader_service=downloader_service,
        package_repository=package_repo
    )
    
    # 创建业务服务（依赖接口）
    release_service = ReleaseService(
        release_repository=release_repo,
        storage_service=storage_service,
        authorization_service=authorization_service
    )
    
    download_service = DownloadService(
        user_repository=user_repo,
        release_repository=release_repo,
        storage_service=storage_service,
        authorization_service=authorization_service
    )
    
    # 返回容器
    class Container:
        auth_service = auth_service
        authorization_service = authorization_service
        storage_service = storage_service
        release_service = release_service
        download_service = download_service
        license_service = license_service
        ...
    
    return Container()
```

## 总结

通过接口和适配器模式，我们成功地将账号系统和存储系统解耦：

1. **账号系统**可以独立运行，只需要 UserRepository 和 LicenseRepository
2. **存储系统**可以独立运行，只需要 PublisherService、DownloaderService 和 PackageRepository
3. **业务服务**通过接口协调两个系统，实现了松耦合

这种架构设计提高了系统的可维护性、可测试性和可扩展性。
