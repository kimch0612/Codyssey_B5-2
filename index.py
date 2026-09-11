# 작성자·키워드 역색인 갱신과 후보 조회 담당
from commit import Commit


class CommitIndex:
    """작성자·키워드로 커밋 ID를 찾는 역색인을 관리한다."""

    def __init__(self) -> None:
        self.author_index: dict[str, set[str]] = {} # 작성자 -> 그 작성자의 커밋 ID 집합
        # e.g. -> { "Alice": {"CI_0", "CI_1", ...}}

    def add_commit(self, commit: Commit) -> None:
        """커밋을 색인에 등록한다."""
        if commit.author not in self.author_index.keys(): # 작성자가 이 색인에 등록되어 있지 않은가?
            self.author_index[commit.author] = set() # 그렇다면 등록하자
        
        self.author_index[commit.author].add(commit.hash) # 작성자 색인에 커밋 해시값을 추가하자

    def find_by_author(self, author: str) -> set[str]:
        """작성자에 해당하는 커밋 ID들을 반환한다."""
        if author not in self.author_index.keys():
            return set()
        
        return self.author_index[author]