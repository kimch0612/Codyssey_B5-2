# 저장소 상태, 초기화, 커밋 생성, 브랜치 생성·전환, 조회 기능 연결 담당
from commit import Commit


class Repository:
    """커밋 저장소와 저장소의 현재 상태를 관리한다."""

    def __init__(self) -> None:
        self._commit_counter: int = 0
        self.commits: dict[str, Commit] = {} # 키는 커밋 ID, 값은 Commit 객체
        self.branches: dict[str, str | None] = {} # 각 브랜치가 가리키는 커밋 ID
        self.head: str | None = None # 현재 브랜치 이름
        self.current_user: str | None = None

    def _generate_commit_hash(self) -> str:
        """현재 세션에서 사용하지 않은 커밋 ID를 생성해 반환한다."""
        _commit_id_prefix = "CI_"

        while True:
            tmp_commit_id = _commit_id_prefix + str(self._commit_counter)
            self._commit_counter += 1
            if tmp_commit_id not in self.commits:
                return tmp_commit_id

    def initialize(self, user_name: str) -> None:
        """main 브랜치, HEAD, 현재 사용자를 설정한다."""
        # 다시 INIT를 하면 main의 커밋 위치가 None으로 바뀌는 등 여러 이슈가 생길 수 있으니 일단은 막자.. 근데 나중에 다시 생각해봐야 할 것 같음
        if self.current_user != None:
            raise ValueError("이미 초기화가 완료된 Repository입니다.")

        self.current_user = user_name
        self.branches["main"] = None # main 브랜치는 있지만 아직 커밋이 없어요
        self.head = "main"

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