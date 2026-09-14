# 비교 기준을 바꿀 수 있는 직접 구현 정렬 담당
from datetime import datetime
from commit import Commit


def get_sort_key(commit: Commit, sort_by: str) -> datetime | str:
    """정렬 기준에 따라 커밋의 생성 시각 또는 작성자 이름을 반환한다."""
    if sort_by == "date":
        return commit.timestamp
    elif sort_by == "author":
        return commit.author
    else:
        raise ValueError("허용되지 않은 정렬 타입이 입력되었습니다.")

def insertion_sort(
    commits: list[Commit],
    sort_by: str,
) -> list[Commit]:
    """원본 목록을 변경하지 않고 지정한 기준의 오름차순으로 정렬한다."""
    result = list(commits)

    for i in range(1, len(result)):
        tmp_commit = result[i]
        tmp_value = get_sort_key(tmp_commit, sort_by)

        j = i - 1
        while j >= 0 and get_sort_key(result[j], sort_by) > tmp_value: # 조건에 맞는 놈을 오른쪽으로 한칸씩 밀어내자
            result[j + 1] = result[j]
            j -= 1
        
        result[j + 1] = tmp_commit

    return result