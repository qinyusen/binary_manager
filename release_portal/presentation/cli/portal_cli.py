import sys
import argparse
import getpass
from pathlib import Path
from ...shared import Config, AuthenticationError, ValidationError, NotFoundError
from ...initializer import create_container, DatabaseInitializer


class PortalCLI:
    def __init__(self):
        self.container = None
        self.config_dir = Path.home() / '.release-portal'
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_token(self):
        if not self.config_file.exists():
            return None
        import json
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        return config.get('token')
    
    def _save_token(self, token, username):
        import json
        config = {
            'token': token,
            'username': username
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _clear_token(self):
        if self.config_file.exists():
            self.config_file.unlink()
    
    def _get_authenticated_user(self):
        token = self._load_token()
        if not token:
            print("Error: Not logged in. Please run 'release-portal login' first.")
            sys.exit(1)
        
        user = self.container.auth_service.get_user_from_token(token)
        if not user:
            print("Error: Invalid or expired token. Please login again.")
            self._clear_token()
            sys.exit(1)
        
        return user
    
    def init(self, args):
        """Initialize database"""
        db_path = args.db if hasattr(args, 'db') and args.db else Config.get_default_db_path()
        print(f"Initializing database at: {db_path}")
        
        initializer = DatabaseInitializer(db_path)
        initializer.initialize()
        
        print("✓ Database initialized successfully")
        print("✓ Default roles created: Admin, Publisher, Customer")
    
    def login(self, args):
        """Login to the portal"""
        self.container = create_container()
        
        username = args.username
        password = getpass.getpass("Password: ")
        
        try:
            token = self.container.auth_service.login(username, password)
            self._save_token(token, username)
            print(f"✓ Logged in as '{username}'")
        except ValueError as e:
            print(f"✗ Login failed: {e}")
            sys.exit(1)
    
    def logout(self, args):
        """Logout from the portal"""
        self._clear_token()
        print("✓ Logged out successfully")
    
    def whoami(self, args):
        """Show current user information"""
        self.container = create_container()
        user = self._get_authenticated_user()
        
        print(f"User ID: {user.user_id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role.name}")
        if user.license_id:
            print(f"License: {user.license_id}")
    
    def register(self, args):
        """Register a new user (admin only)"""
        self.container = create_container()
        user = self._get_authenticated_user()
        
        if user.role.name != 'Admin':
            print("✗ Only administrators can register new users")
            sys.exit(1)
        
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("✗ Passwords do not match")
            sys.exit(1)
        
        try:
            new_user = self.container.auth_service.register(
                username=args.username,
                email=args.email,
                password=password,
                role_id=args.role_id,
                license_id=args.license_id
            )
            print(f"✓ User '{new_user.username}' registered successfully")
            print(f"  User ID: {new_user.user_id}")
        except ValueError as e:
            print(f"✗ Registration failed: {e}")
            sys.exit(1)
    
    def publish(self, args):
        """Publish a new release"""
        self.container = create_container()
        user = self._get_authenticated_user()
        
        if not user.has_permission('publish', args.type.upper()):
            print(f"✗ You don't have permission to publish {args.type} resources")
            sys.exit(1)
        
        from ...domain.value_objects import ResourceType, ContentType
        
        try:
            release = self.container.release_service.create_draft(
                resource_type=ResourceType.from_string(args.type),
                version=args.version,
                publisher_id=user.user_id,
                description=args.description,
                changelog=args.changelog
            )
            
            print(f"✓ Created draft release: {release.release_id}")
            
            if args.source_dir:
                print(f"Publishing source package...")
                pkg_id = self.container.release_service.add_package(
                    release.release_id,
                    ContentType.SOURCE,
                    args.source_dir
                )
                print(f"  ✓ Source package ID: {pkg_id}")
            
            if args.binary_dir:
                print(f"Publishing binary package...")
                pkg_id = self.container.release_service.add_package(
                    release.release_id,
                    ContentType.BINARY,
                    args.binary_dir
                )
                print(f"  ✓ Binary package ID: {pkg_id}")
            
            if args.doc_dir:
                print(f"Publishing document package...")
                pkg_id = self.container.release_service.add_package(
                    release.release_id,
                    ContentType.DOCUMENT,
                    args.doc_dir
                )
                print(f"  ✓ Document package ID: {pkg_id}")
            
            if not args.draft:
                # 检查是否需要运行测试
                run_tests = getattr(args, 'test', False)
                test_level = getattr(args, 'test_level', 'critical')
                
                self.container.release_service.publish_release(
                    release.release_id,
                    user_id=user.user_id,
                    run_tests=run_tests,
                    test_level=test_level
                )
                print(f"✓ Release published successfully")
            else:
                print(f"✓ Draft saved. Use 'release-portal publish --release-id {release.release_id} --publish' to publish")
        
        except Exception as e:
            print(f"✗ Publish failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def list(self, args):
        """List releases"""
        self.container = create_container()
        
        from ...domain.value_objects import ResourceType
        
        resource_type = ResourceType.from_string(args.type) if args.type else None
        
        releases = self.container.release_service.list_releases(
            resource_type=resource_type,
            status=args.status
        )
        
        if not releases:
            print("No releases found")
            return
        
        print(f"\n{'Release ID':<20} {'Type':<10} {'Version':<12} {'Status':<10} {'Published'}")
        print("-" * 80)
        
        for release in releases:
            published = release.published_at.strftime('%Y-%m-%d') if release.published_at else 'N/A'
            print(f"{release.release_id:<20} {release.resource_type.value:<10} {release.version:<12} {release.status.value:<10} {published}")
    
    def download(self, args):
        """Download packages"""
        self.container = create_container()
        user = self._get_authenticated_user()
        
        try:
            packages = self.container.download_service.get_available_packages(user.user_id, args.release_id)
            
            if not packages:
                print("No packages available for download")
                return
            
            output_dir = args.output or f"./downloads/{args.release_id}"
            
            print(f"Available packages:")
            for pkg in packages:
                print(f"  - {pkg['content_type']}: {pkg['package_name']} v{pkg['version']} ({pkg['size']} bytes)")
            
            if args.content_type:
                from ...domain.value_objects import ContentType
                ct = ContentType.from_string(args.content_type)
                package_id = None
                for pkg in packages:
                    if pkg['content_type'] == str(ct):
                        package_id = pkg['package_id']
                        break
                
                if not package_id:
                    print(f"✗ Content type '{args.content_type}' not available")
                    sys.exit(1)
                
                self.container.download_service.download_package(user.user_id, args.release_id, args.content_type, output_dir)
                print(f"✓ Downloaded to: {output_dir}")
            else:
                for pkg in packages:
                    self.container.download_service.download_package(user.user_id, args.release_id, pkg['content_type'], output_dir)
                print(f"✓ Downloaded {len(packages)} package(s) to: {output_dir}")
        
        except Exception as e:
            print(f"✗ Download failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def license_create(self, args):
        """Create a new license (admin only)"""
        self.container = create_container()
        user = self._get_authenticated_user()
        
        if user.role.name != 'Admin':
            print("✗ Only administrators can create licenses")
            sys.exit(1)
        
        from datetime import datetime
        from ...domain.value_objects import AccessLevel, ResourceType
        
        expires_at = None
        if args.expires_at:
            expires_at = datetime.fromisoformat(args.expires_at)
        
        resource_types = [ResourceType.from_string(rt.strip()) for rt in args.resource_types.split(',')]
        
        try:
            license = self.container.license_service.create_license(
                organization=args.organization,
                access_level=AccessLevel.from_string(args.access_level),
                allowed_resource_types=resource_types,
                expires_at=expires_at,
                metadata={'notes': args.notes} if args.notes else {}
            )
            
            print(f"✓ License created successfully")
            print(f"  License ID: {license.license_id}")
            print(f"  Organization: {license.organization}")
            print(f"  Access Level: {license.access_level.value}")
            print(f"  Resource Types: {', '.join([rt.value for rt in license.allowed_resource_types])}")
            if license.expires_at:
                print(f"  Expires: {license.expires_at.strftime('%Y-%m-%d')}")
        
        except Exception as e:
            print(f"✗ License creation failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    cli = PortalCLI()
    
    parser = argparse.ArgumentParser(description='Release Portal CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.add_argument('--db', help='Database path')
    init_parser.set_defaults(func=cli.init)
    
    # Auth commands
    login_parser = subparsers.add_parser('login', help='Login to the portal')
    login_parser.add_argument('--username', required=True, help='Username')
    login_parser.set_defaults(func=cli.login)
    
    logout_parser = subparsers.add_parser('logout', help='Logout from the portal')
    logout_parser.set_defaults(func=cli.logout)
    
    whoami_parser = subparsers.add_parser('whoami', help='Show current user')
    whoami_parser.set_defaults(func=cli.whoami)
    
    register_parser = subparsers.add_parser('register', help='Register a new user (admin only)')
    register_parser.add_argument('--username', required=True, help='Username')
    register_parser.add_argument('--email', required=True, help='Email')
    register_parser.add_argument('--role-id', required=True, help='Role ID')
    register_parser.add_argument('--license-id', help='License ID (for customers)')
    register_parser.set_defaults(func=cli.register)
    
    # Publish commands
    publish_parser = subparsers.add_parser('publish', help='Publish a new release')
    publish_parser.add_argument('--type', required=True, choices=['bsp', 'driver', 'examples'], help='Resource type')
    publish_parser.add_argument('--version', required=True, help='Version (e.g., v1.0.0)')
    publish_parser.add_argument('--source-dir', help='Source directory')
    publish_parser.add_argument('--binary-dir', help='Binary directory')
    publish_parser.add_argument('--doc-dir', help='Documentation directory')
    publish_parser.add_argument('--description', help='Description')
    publish_parser.add_argument('--changelog', help='Changelog')
    publish_parser.add_argument('--draft', action='store_true', help='Save as draft')
    publish_parser.add_argument('--test', action='store_true', help='Run tests before publishing')
    publish_parser.add_argument('--test-level', choices=['critical', 'all', 'api', 'integration'], 
                                default='critical', help='Test level (default: critical)')
    publish_parser.set_defaults(func=cli.publish)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List releases')
    list_parser.add_argument('--type', choices=['bsp', 'driver', 'examples'], help='Filter by type')
    list_parser.add_argument('--status', choices=['DRAFT', 'PUBLISHED', 'ARCHIVED'], help='Filter by status')
    list_parser.set_defaults(func=cli.list)
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download packages')
    download_parser.add_argument('--release-id', required=True, help='Release ID')
    download_parser.add_argument('--content-type', choices=['SOURCE', 'BINARY', 'DOCUMENT'], help='Content type')
    download_parser.add_argument('--output', help='Output directory')
    download_parser.set_defaults(func=cli.download)
    
    # License commands
    license_create_parser = subparsers.add_parser('license-create', help='Create a new license (admin only)')
    license_create_parser.add_argument('--organization', required=True, help='Organization name')
    license_create_parser.add_argument('--access-level', required=True, choices=['FULL_ACCESS', 'BINARY_ACCESS'], help='Access level')
    license_create_parser.add_argument('--resource-types', required=True, help='Comma-separated resource types (e.g., BSP,DRIVER)')
    license_create_parser.add_argument('--expires-at', help='Expiration date (ISO format)')
    license_create_parser.add_argument('--notes', help='Additional notes')
    license_create_parser.set_defaults(func=cli.license_create)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
