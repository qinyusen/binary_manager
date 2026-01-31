import subprocess
import re
from pathlib import Path
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitIntegration:
    """Git集成工具，用于提取Git仓库信息"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
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
            logger.error(f"Git command failed: {e.stderr}")
            return ""
    
    def get_git_info(self) -> Dict:
        """获取Git仓库完整信息"""
        return {
            'commit_hash': self.get_commit_hash(),
            'commit_short': self.get_commit_short(),
            'branch': self.get_branch(),
            'tag': self.get_tag(),
            'author': self.get_author(),
            'author_email': self.get_author_email(),
            'commit_time': self.get_commit_time(),
            'is_dirty': self.is_dirty()
        }
    
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
            return branch if branch != 'HEAD' else None
        except:
            return None
    
    def get_tag(self) -> Optional[str]:
        """获取最新的tag（如果有）"""
        try:
            tag = self._run_git_command('describe --tags --abbrev=0 --exact-match 2>/dev/null')
            return tag if tag else None
        except:
            return None
    
    def get_author(self) -> str:
        """获取作者姓名"""
        return self._run_git_command('log -1 --pretty=format:%an')
    
    def get_author_email(self) -> str:
        """获取作者邮箱"""
        return self._run_git_command('log -1 --pretty=format:%ae')
    
    def get_commit_time(self) -> str:
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
        except:
            return False
    
    def get_changed_files(self, commit: Optional[str] = None) -> List[str]:
        if commit:
            result = self._run_git_command(f'diff --name-only {commit}^ {commit}')
            return result.split('\n') if result else []
        result = self._run_git_command('ls-files')
        return result.split('\n') if result else []
    
    def get_remotes(self) -> list:
        """获取远程仓库URL"""
        try:
            output = self._run_git_command('remote -v')
            remotes = []
            for line in output.split('\n'):
                if line:
                    name, url, _ = line.split()
                    remotes.append({'name': name, 'url': url})
            return remotes
        except:
            return []
    
    def validate_git_repo(self) -> bool:
        """验证是否为有效的Git仓库"""
        try:
            self._run_git_command('rev-parse --git-dir')
            return True
        except:
            return False


def extract_git_info(repo_path: str) -> Dict:
    """提取Git仓库信息的便捷函数"""
    git = GitIntegration(repo_path)
    
    if not git.validate_git_repo():
        logger.warning(f"Not a valid Git repository: {repo_path}")
        return {}
    
    return git.get_git_info()


if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        git_info = extract_git_info(repo_path)
        print(json.dumps(git_info, indent=2))
    else:
        print("Usage: python git_integration.py <repo_path>")
