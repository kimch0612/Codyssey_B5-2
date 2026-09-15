# REPL, 명령 파싱, 입력 검증, 명령 실행 연결, 결과 출력 담당
import shlex

from commit import Commit
from sorting import insertion_sort


def parse_command_line(line: str) -> list[str]:
    """따옴표를 고려해 명령행을 나누고 명령어만 대문자로 정규화한다."""
    line = shlex.split(line) # 'CoMmIt "Add login feature"' -> ['CoMmIt', 'Add login feature']
    if line:
        line[0] = line[0].upper()
    
    return line

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

def format_sorted_log(
    commits: dict[str, Commit],
    sort_by: str,
) -> str:
    """전체 커밋을 지정한 기준으로 정렬해 로그 문자열로 구성한다."""
    commit_list = list(commits.values())
    sorted_commits = insertion_sort(commit_list, sort_by)
    sorted_hash = [c.hash for c in sorted_commits]
    
    return format_log(commits, sorted_hash)
