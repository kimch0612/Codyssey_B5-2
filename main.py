# REPL, 명령 파싱, 입력 검증, 명령 실행 연결, 결과 출력 담당
import shlex

from commit import Commit
from repository import Repository
from sorting import insertion_sort


def parse_command_line(line: str) -> list[str]:
    """따옴표를 고려해 명령행을 나누고 명령어만 대문자로 정규화한다."""
    line = shlex.split(line) # 'CoMmIt "Add login feature"' -> ['CoMmIt', 'Add login feature']
    if line:
        line[0] = line[0].upper()
    
    return line

def parse_author_option(option: str) -> str:
    """`--author=<name>` 옵션에서 작성자 이름을 꺼내 반환한다."""
    prefix = "--author="
    if option.startswith(prefix):
        author = option[len(prefix):]
        if not author.strip():
            raise ValueError("이름이 비어있습니다.")
        return author
    else:
        raise ValueError("잘못된 옵션값이 들어왔습니다.")

def parse_sort_option(option: str) -> str:
    """`--sort-by=date|author` 옵션에서 유효한 정렬 기준을 반환한다."""
    prefix = '--sort-by='
    if option.startswith(prefix):
        sort_type = option[len(prefix):]
        if not sort_type.strip():
            raise ValueError("정렬 기준값이 비었습니다.")
        elif sort_type not in ["date", "author"]:
            raise ValueError("잘못된 정렬 기준값이 들어왔습니다.")
        return sort_type
    else:
        raise ValueError("잘못된 옵션값이 들어왔습니다.")

def validate_argument_count(parts: list[str]) -> None:
    """명령어별 허용 인자 개수인지 검사하고, 잘못되면 ValueError를 발생시킨다."""
    # e.g. parts = ["PATH", "CI_0", "CI_2"]
    if not parts:
        return
    
    valid_arg_counts: dict[str, set[int]] = {
        "INIT": {1},
        "BRANCH": {1},
        "SWITCH": {1},
        "COMMIT": {1},
        "LOG": {0, 1}, # LOG만 옵션이 없는 경우와 옵션 하나가 있는 경우를 모두 허용
        "PATH": {2},
        "ANCESTORS": {1},
        "SEARCH": {1},
        "EXIT": {0},
        "QUIT": {0},
    }

    command = parts[0]
    arg_count = len(parts) - 1

    if command not in valid_arg_counts:
        raise ValueError("존재하지 않는 커맨드를 입력했습니다.")
    elif arg_count not in valid_arg_counts[command]:
        raise ValueError(f"인자의 개수가 잘못됐습니다; 입력:{arg_count}, 필요:{valid_arg_counts[command]}")
    
    return None

def execute_command(repository: Repository, parts: list[str]) -> str:
    """파싱된 명령 하나를 저장소 기능에 연결하고 출력용 문자열을 반환한다."""
    # e.g. parts = ["INIT", "Alice Kim"]
    validate_argument_count(parts)

    if not parts:
        return ""

    command = parts[0]

    if command == "INIT":
        user_name = parts[1]
        if not user_name.strip():
            raise ValueError("사용자 이름이 비어 있습니다.")
            
        repository.initialize(user_name)
        return f"Initialized repository.\nCurrent branch: {repository.head}\nCurrent user: {repository.current_user}"

    if command == "BRANCH":
        branch_name = parts[1]
        if not branch_name.strip():
            raise ValueError("브랜치 이름이 비어있습니다.")

        repository.create_branch(branch_name)
        return f"Created branch: {branch_name}"

    if command == "SWITCH":
        branch_name = parts[1]
        if not branch_name.strip():
            raise ValueError("브랜치 이름이 비어있습니다.")
        
        repository.switch_branch(branch_name)
        return f"Branch switched: {repository.head}"

    raise NotImplementedError("아직 연결하지 않은 명령입니다.")

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
