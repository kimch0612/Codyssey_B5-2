# REPL, 명령 파싱, 입력 검증, 명령 실행 연결, 결과 출력 담당
from commit import Commit


def format_log(
    commits: dict[str, Commit],
    ordered_ids: list[str],
) -> str:
    """주어진 ID 순서대로 커밋 정보를 로그 문자열로 구성한다."""
    result = []

    for hash in ordered_ids:
        commit = commits[hash]
        c_author = commit.author
        c_timestamp = commit.timestamp
        c_message = commit.message

        tmp_result = f"commit {hash} ({c_author}, {c_timestamp})\n{c_message}"
        result.append(tmp_result)
    
    if not result: return ""
    else: return "\n".join(result)