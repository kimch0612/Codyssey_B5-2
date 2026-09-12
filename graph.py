# 부모 우선 순서, 조상 탐색, 최단 경로 탐색 담당
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
    
    # 내용 이해가 잘 안 됨
    # 나중에 DFS, BFS 공부하면서 다시 살펴봐야 할 것 같음