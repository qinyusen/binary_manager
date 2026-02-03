from typing import Optional
from datetime import datetime


class GitInfo:
    def __init__(
        self,
        commit_hash: str,
        commit_short: str,
        branch: Optional[str] = None,
        tag: Optional[str] = None,
        author: Optional[str] = None,
        author_email: Optional[str] = None,
        commit_time: Optional[str] = None,
        is_dirty: bool = False
    ):
        self._commit_hash = commit_hash
        self._commit_short = commit_short
        self._branch = branch
        self._tag = tag
        self._author = author
        self._author_email = author_email
        self._commit_time = commit_time
        self._is_dirty = is_dirty
    
    @property
    def commit_hash(self) -> str:
        return self._commit_hash
    
    @property
    def commit_short(self) -> str:
        return self._commit_short
    
    @property
    def branch(self) -> Optional[str]:
        return self._branch
    
    @property
    def tag(self) -> Optional[str]:
        return self._tag
    
    @property
    def author(self) -> Optional[str]:
        return self._author
    
    @property
    def author_email(self) -> Optional[str]:
        return self._author_email
    
    @property
    def commit_time(self) -> Optional[str]:
        return self._commit_time
    
    @property
    def is_dirty(self) -> bool:
        return self._is_dirty
    
    def to_dict(self) -> dict:
        return {
            'commit_hash': self._commit_hash,
            'commit_short': self._commit_short,
            'branch': self._branch,
            'tag': self._tag,
            'author': self._author,
            'author_email': self._author_email,
            'commit_time': self._commit_time,
            'is_dirty': self._is_dirty
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GitInfo':
        return cls(
            commit_hash=data.get('commit_hash', ''),
            commit_short=data.get('commit_short', ''),
            branch=data.get('branch'),
            tag=data.get('tag'),
            author=data.get('author'),
            author_email=data.get('author_email'),
            commit_time=data.get('commit_time'),
            is_dirty=data.get('is_dirty', False)
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, GitInfo):
            return False
        return self._commit_hash == other._commit_hash
    
    def __hash__(self) -> int:
        return hash(self._commit_hash)
    
    def __repr__(self) -> str:
        return f"GitInfo(commit_short='{self._commit_short}', branch='{self._branch}')"
