# 커밋 한 개의 정보 표현 담당
from datetime import datetime


class Commit:
    """커밋 한 개의 메타데이터와 부모 관계를 표현한다."""
    def __init__(
        self,
        commit_hash: str,
        message: str,
        author: str,
        timestamp: datetime,
        parents: list[str],
    ) -> None:
        self.hash = commit_hash
        self.message = message
        self.author = author
        self.timestamp = timestamp
        self.parents = parents