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