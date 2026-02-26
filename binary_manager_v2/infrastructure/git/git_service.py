import subprocess
from pathlib import Path
from typing import Optional, List
from ...domain.value_objects import GitInfo
from ...shared.logger import Logger


class GitService:
    """Git服务，用于提取Git仓库信息"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        self.logger = Logger.get(self.__class__.__name__)
    
    def _run_git_command(self, command: str) -> str:
        """执行Git命令并返回输出"""
        try:
            result = subprocess.run(
                ['git'] + command.split(),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e.stderr}")
            return ""
        except FileNotFoundError:
            self.logger.error("Git is not installed or not in PATH")
            return ""
    
    def get_git_info(self) -> Optional[GitInfo]:
        """获取Git仓库完整信息"""
        if not self.is_git_repo():
            self.logger.warning(f"Not a valid Git repository: {self.repo_path}")
            return None
        
        try:
            return GitInfo(
                commit_hash=self.get_commit_hash(),
                commit_short=self.get_commit_short(),
                branch=self.get_branch(),
                tag=self.get_tag(),
                author=self.get_author(),
                author_email=self.get_author_email(),
                commit_message=self.get_commit_message(),
                commit_time=self.get_commit_time(),
                is_dirty=self.is_dirty(),
                remotes=self.get_remotes()
            )
        except Exception as e:
            self.logger.error(f"Failed to get git info: {e}")
            return None
    
    def get_commit_hash(self) -> str:
        """获取完整的commit哈希"""
        return self._run_git_command('rev-parse HEAD')
    
    def get_commit_short(self) -> str:
        """获取短哈希"""
        return self._run_git_command('rev-parse --short HEAD')
    
    def get_branch(self) -> Optional[str]:
        """获取当前分支名称"""
        try:
            branch = self._run_git_command('rev-parse --abbrev-ref HEAD')
            return branch if branch and branch != 'HEAD' else None
        except Exception:
            return None
    
    def get_tag(self) -> Optional[str]:
        """获取最新的tag（如果有）"""
        try:
            tag = self._run_git_command('describe --tags --abbrev=0 --exact-match 2>/dev/null || true')
            return tag if tag else None
        except Exception:
            return None
    
    def get_author(self) -> str:
        """获取作者姓名"""
        return self._run_git_command('log -1 --pretty=format:%an')
    
    def get_author_email(self) -> str:
        """获取作者邮箱"""
        return self._run_git_command('log -1 --pretty=format:%ae')
    
    def get_commit_time(self) -> str:
        """获取提交时间"""
        time_str = self._run_git_command('log -1 --pretty=format:%ci')
        if time_str:
            return time_str.replace(' ', 'T') + 'Z'
        return ""
    
    def get_commit_message(self) -> str:
        """获取提交信息"""
        return self._run_git_command('log -1 --pretty=format:%s')
    
    def is_dirty(self) -> bool:
        """检查是否有未提交的更改"""
        try:
            status = self._run_git_command('status --porcelain')
            return len(status) > 0
        except Exception:
            return False
    
    def get_changed_files(self, commit: Optional[str] = None) -> List[str]:
        """获取更改的文件列表"""
        if commit:
            result = self._run_git_command(f'diff --name-only {commit}^ {commit}')
        else:
            result = self._run_git_command('ls-files')
        return result.split('\n') if result else []
    
    def get_remotes(self) -> List[dict]:
        """获取远程仓库URL"""
        try:
            output = self._run_git_command('remote -v')
            remotes = []
            for line in output.split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        remotes.append({'name': parts[0], 'url': parts[1]})
            return remotes
        except Exception:
            return []
    
    def is_git_repo(self) -> bool:
        """验证是否为有效的Git仓库"""
        try:
            result = self._run_git_command('rev-parse --git-dir')
            return bool(result)
        except Exception:
            return False
    
    def validate_git_repo(self, require_clean: bool = False) -> bool:
        """验证Git仓库状态"""
        if not self.is_git_repo():
            return False
        
        if require_clean and self.is_dirty():
            self.logger.warning("Git repository has uncommitted changes")
            return False
        
        return True
    
    def get_current_commit(self) -> Optional[str]:
        """获取当前commit哈希的便捷方法"""
        return self.get_commit_hash() or None
    
    def get_file_content(self, file_path: str, commit: Optional[str] = None) -> Optional[str]:
        """获取指定commit时的文件内容"""
        try:
            if commit:
                return self._run_git_command(f'show {commit}:{file_path}')
            else:
                return self._run_git_command(f'show HEAD:{file_path}')
        except Exception:
            return None
    
    def get_diff(self, commit1: Optional[str] = None, commit2: Optional[str] = None) -> str:
        """获取两个commit之间的差异"""
        try:
            if commit1 and commit2:
                return self._run_git_command(f'diff {commit1} {commit2}')
            elif commit1:
                return self._run_git_command(f'diff {commit1}')
            else:
                return self._run_git_command('diff')
        except Exception:
            return ""
