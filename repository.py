# 저장소 상태, 초기화, 커밋 생성, 브랜치 생성·전환, 조회 기능 연결 담당
from commit import Commit


class Repository:
    """커밋 저장소와 저장소의 현재 상태를 관리한다."""

    def __init__(self) -> None:
        self._commit_counter: int = 0
        self.commits: dict[str, Commit] = {} # 키는 커밋 ID, 값은 Commit 객체

    def _generate_commit_hash(self) -> str:
        """현재 세션에서 사용하지 않은 커밋 ID를 생성해 반환한다."""
        _commit_id_prefix = "CI_"

        while True:
            tmp_commit_id = _commit_id_prefix + str(self._commit_counter)
            self._commit_counter += 1
            if tmp_commit_id not in self.commits:
                return tmp_commit_id

    def store_commit(self, commit: Commit) -> None:
        """커밋을 저장한다. 이미 사용 중인 ID는 허용하지 않는다."""
        if commit.hash in self.commits:
            raise ValueError("이미 존재하는 커밋 ID입니다.")

        self.commits[commit.hash] = commit

    def get_commit(self, commit_hash: str) -> Commit:
        """ID에 해당하는 커밋을 반환한다."""
        if commit_hash in self.commits:
            return self.commits[commit_hash]
        
        raise ValueError("존재하지 않는 커밋 ID를 찾으려 했습니다.")