# 부모 우선 순서, 조상 탐색, 최단 경로 탐색 담당
# 이 파일에 있는 기능들은 자료구조랑 직접적인 연관이 있어서 그런가, 이해가 잘 안 됨
# 평가 받기 전에 다시 리마인드 및 재공부가 필요할 것 같음
from commit import Commit


def find_ancestors(
    commits: dict[str, Commit],
    commit_hash: str,
) -> set[str]:
    """부모 방향으로 도달 가능한 모든 조상의 ID를 반환한다."""
    if commit_hash not in commits:
        raise ValueError("존재하지 않는 커밋 ID로 부모를 찾으려 했습니다.")
    
    start_commit = commits[commit_hash]
    parent_list = list(start_commit.parents) # 발견했지만, 이 커밋의 부모들은 아직 확인하지 않은 ID 목록
    parent_set = set(start_commit.parents)   # 지금까지 발견한 모든 조상 ID (중복 방지용)

    while parent_list: # bfs 형식으로 찾아보자
        parent = parent_list.pop(0)
        parent_commit = commits[parent]
        for parent in parent_commit.parents:
            if parent not in parent_set:
                parent_list.append(parent)
                parent_set.add(parent)

    return parent_set

def build_children_map(
    commits: dict[str, Commit],
) -> dict[str, list[str]]:
    """각 커밋 ID를 직접 자식 ID 목록에 연결하며, 자식이 없으면 빈 목록을 둔다."""
    result: dict[str, list[str]] = {}

    # 1. 모든 커밋의 자식 목록을 먼저 준비한다.
    # 다른 커밋의 부모로 등장하지 않는 커밋도 결과에 포함된다.
    for commit_id in commits:
        result[commit_id] = []

    # 2. 자식의 부모 정보를 읽고, 부모의 자식 목록에 연결을 추가한다.
    # 예: B의 부모가 A라면 result["A"]에 "B"를 추가한다.
    for commit in commits.values():
        for parent_id in commit.parents:
            result[parent_id].append(commit.hash)

    return result

def build_parent_counts(
    commits: dict[str, Commit],
) -> dict[str, int]:
    """각 커밋 ID를 직접 부모 수에 연결한 초기 개수 표를 반환한다."""
    result = {}
    for commit in commits.values():
        result[commit.hash] = len(commit.parents)
    
    return result

def topological_order(
    commits: dict[str, Commit],
) -> list[str]:
    """모든 부모가 자식보다 먼저 나오는 커밋 ID 순서를 반환한다."""
    pass