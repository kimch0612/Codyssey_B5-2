# B5-2 Mini Git 명령별 호출 흐름

이 문서는 사용자가 `mini-git>` 프롬프트에 명령을 입력한 뒤 어떤 함수와 객체를 거쳐 결과가 출력되는지 정리한다.

기준 소스는 [main.py](../main.py), [repository.py](../repository.py), [commit.py](../commit.py), [graph.py](../graph.py), [index.py](../index.py), [sorting.py](../sorting.py)다. 아래 흐름은 현재 코드의 실제 호출 관계를 나타낸다.

## 0. 모든 명령이 공유하는 REPL 흐름

프로그램을 시작하면 `run_repl()`이 `Repository` 객체를 한 번 만든다. 같은 실행 세션의 모든 명령은 이 객체를 계속 공유한다.

```text
main.py: run_repl()
  │
  ├─ Repository()
  │    │
  │    ├─ commits = {}
  │    ├─ branches = {}
  │    ├─ head = None
  │    ├─ current_user = None
  │    ├─ _commit_counter = 0
  │    └─ CommitIndex()
  │         ├─ author_index = {}
  │         └─ keyword_index = {}
  │
  └─ while True
       │
       ├─ input("mini-git> ")
       ├─ parse_command_line(line)
       │    ├─ shlex.split(line)
       │    └─ 첫 번째 토큰인 명령어만 upper() 적용
       │
       ├─ 빈 입력이면 continue
       ├─ EXIT 또는 QUIT이면 인자 수 확인 후 break
       │
       ├─ execute_command(repository, parts)
       │    └─ 명령에 맞는 저장소·그래프·검색·정렬 함수 호출
       │
       ├─ 반환 문자열이 비어 있지 않으면 print(result)
       │
       └─ ValueError가 발생하면
            ├─ print(f"[오류] {e}")
            └─ 프로그램을 종료하지 않고 다음 입력으로 이동
```

`parse_command_line()`은 명령어만 대문자로 바꾼다. 사용자명, 브랜치명, 메시지, 작성자명 같은 나머지 문자열의 대소문자는 그대로 유지된다.

---

## 1. INIT

입력 예시:

```text
init "Alice Kim"
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line('init "Alice Kim"')
  │    └─ ["INIT", "Alice Kim"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    │    └─ INIT의 인자가 정확히 1개인지 확인
  │    │
  │    ├─ user_name.strip()으로 빈 이름인지 확인
  │    │
  │    ├─ Repository.initialize("Alice Kim")
  │    │    │
  │    │    ├─ current_user가 이미 설정됐는지 확인
  │    │    ├─ current_user = "Alice Kim"
  │    │    ├─ branches["main"] = None
  │    │    └─ head = "main"
  │    │
  │    └─ 초기화 결과 문자열 반환
  │
  └─ print(result)
```

초기화 직후의 핵심 상태:

```text
current_user == "Alice Kim"
head == "main"
branches == {"main": None}
commits == {}
```

`None`은 `main` 브랜치는 존재하지만 아직 가리키는 커밋이 없다는 뜻이다. 반복 `INIT`은 `Repository.initialize()`에서 `ValueError`가 발생한다.

---

## 2. BRANCH

입력 예시:

```text
branch feature
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("branch feature")
  │    └─ ["BRANCH", "feature"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ branch_name.strip()으로 빈 이름인지 확인
  │    │
  │    ├─ Repository.create_branch("feature")
  │    │    │
  │    │    ├─ 저장소가 초기화됐는지 확인
  │    │    ├─ 같은 이름의 브랜치가 있는지 확인
  │    │    ├─ branches[head]에서 현재 커밋 ID를 읽음
  │    │    └─ branches["feature"] = branches[head]
  │    │
  │    └─ "Created branch: feature" 반환
  │
  └─ print(result)
```

이 명령은 커밋을 복사하거나 `head`를 바꾸지 않는다. 새 브랜치 이름이 현재 브랜치와 같은 커밋 ID를 가리키게 할 뿐이다.

예를 들어 실행 전 상태가 다음과 같다면:

```text
head == "main"
branches == {"main": "CI_0"}
```

실행 후에는 다음과 같다.

```text
head == "main"
branches == {"main": "CI_0", "feature": "CI_0"}
```

---

## 3. SWITCH

입력 예시:

```text
switch feature
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("switch feature")
  │    └─ ["SWITCH", "feature"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ branch_name.strip()으로 빈 이름인지 확인
  │    │
  │    ├─ Repository.switch_branch("feature")
  │    │    │
  │    │    ├─ 저장소가 초기화됐는지 확인
  │    │    ├─ branches에 "feature"가 있는지 확인
  │    │    └─ head = "feature"
  │    │
  │    └─ "Branch switched: feature" 반환
  │
  └─ print(result)
```

`SWITCH`는 `head`에 저장된 브랜치 이름만 바꾼다. 커밋 객체, 부모 관계, 각 브랜치가 가리키는 커밋 ID는 수정하지 않는다.

---

## 4. COMMIT

입력 예시:

```text
commit "Add login feature"
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line('commit "Add login feature"')
  │    └─ ["COMMIT", "Add login feature"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ commit_message.strip()으로 빈 메시지인지 확인
  │    │
  │    ├─ Repository.create_commit("Add login feature")
  │    │    │
  │    │    ├─ 저장소가 초기화됐는지 확인
  │    │    │
  │    │    ├─ Repository._generate_commit_hash()
  │    │    │    ├─ _commit_counter로 "CI_0", "CI_1", ... 후보 생성
  │    │    │    ├─ 카운터를 1 증가
  │    │    │    └─ commits에 없는 ID를 반환
  │    │    │
  │    │    ├─ branches[head]에서 현재 커밋 ID를 읽음
  │    │    │    ├─ 값이 None이면 parents = []
  │    │    │    └─ ID가 있으면 parents = [현재 커밋 ID]
  │    │    │
  │    │    ├─ Commit(
  │    │    │      commit_hash=새 ID,
  │    │    │      message="Add login feature",
  │    │    │      author=current_user,
  │    │    │      timestamp=datetime.now(),
  │    │    │      parents=parents,
  │    │    │  )
  │    │    │
  │    │    ├─ Repository.store_commit(new_commit)
  │    │    │    ├─ 같은 ID가 이미 있는지 확인
  │    │    │    └─ commits[new_commit.hash] = new_commit
  │    │    │
  │    │    ├─ branches[head] = new_commit.hash
  │    │    │
  │    │    ├─ CommitIndex.add_commit(new_commit)
  │    │    │    ├─ author_index[author]에 커밋 ID 추가
  │    │    │    ├─ message.lower().split()으로 토큰 생성
  │    │    │    └─ 각 keyword_index[token]에 커밋 ID 추가
  │    │    │
  │    │    └─ 새 Commit 객체 반환
  │    │
  │    └─ "[현재 브랜치 새 ID] 메시지" 문자열 반환
  │
  └─ print(result)
```

`COMMIT` 한 번으로 다음 세 상태가 같은 새 ID를 가리키게 된다.

```text
commits[새 ID]       → 새 Commit 객체
branches[head]       → 새 ID
commit_index의 집합들 → 새 ID 포함
```

---

## 5. 기본 LOG

입력 예시:

```text
log
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("log")
  │    └─ ["LOG"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ 저장소가 초기화됐는지 확인
  │    │
  │    ├─ topological_order(repository.commits)
  │    │    │
  │    │    ├─ build_children_map(commits)
  │    │    │    ├─ 모든 ID에 빈 자식 목록 준비
  │    │    │    └─ 각 Commit.parents를 읽어 부모 → 자식 관계 추가
  │    │    │
  │    │    ├─ build_parent_counts(commits)
  │    │    │    └─ 각 ID에 직접 부모 수 저장
  │    │    │
  │    │    ├─ 부모 수가 0인 ID들을 ready에 추가
  │    │    │
  │    │    ├─ ready가 빌 때까지 반복
  │    │    │    ├─ ready.pop()으로 현재 ID 선택
  │    │    │    ├─ ordered_ids에 현재 ID 추가
  │    │    │    ├─ 직접 자식들의 남은 부모 수를 1씩 감소
  │    │    │    └─ 남은 부모 수가 0이 된 자식을 ready에 추가
  │    │    │
  │    │    └─ 부모 우선 ordered_ids 반환
  │    │
  │    ├─ format_log(repository.commits, ordered_ids)
  │    │    ├─ ID 순서대로 Commit 객체 조회
  │    │    ├─ hash, author, timestamp, message를 문자열로 구성
  │    │    └─ 각 커밋 문자열을 줄바꿈으로 연결
  │    │
  │    └─ 완성된 로그 문자열 반환
  │
  └─ 결과가 비어 있지 않으면 print(result)
```

기본 `LOG`는 현재 브랜치에서만 도달 가능한 커밋이 아니라 `repository.commits`에 들어 있는 전체 커밋을 대상으로 한다. `ready.pop()`을 사용하므로 형제 커밋끼리의 순서는 고정하지 않지만, 모든 부모가 자식보다 먼저 나온다.

---

## 6. 정렬 LOG

입력 예시:

```text
log --sort-by=date
log --sort-by=author
```

두 명령은 같은 흐름을 사용하고 `get_sort_key()`가 반환하는 값만 다르다.

```text
main.py: run_repl()
  │
  ├─ parse_command_line("log --sort-by=date")
  │    └─ ["LOG", "--sort-by=date"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ 저장소가 초기화됐는지 확인
  │    │
  │    ├─ parse_sort_option("--sort-by=date")
  │    │    ├─ "--sort-by=" 접두사 확인
  │    │    ├─ 값이 비어 있는지 확인
  │    │    ├─ date 또는 author인지 확인
  │    │    └─ "date" 반환
  │    │
  │    ├─ format_sorted_log(repository.commits, "date")
  │    │    │
  │    │    ├─ list(commits.values())
  │    │    │    └─ Commit 객체 목록 생성
  │    │    │
  │    │    ├─ insertion_sort(commit_list, "date")
  │    │    │    ├─ 원본 목록을 복사
  │    │    │    ├─ 두 번째 Commit부터 차례로 삽입 위치 탐색
  │    │    │    ├─ get_sort_key(commit, "date")
  │    │    │    │    └─ commit.timestamp 반환
  │    │    │    ├─ 더 큰 키를 가진 앞 원소를 오른쪽으로 이동
  │    │    │    └─ 정렬된 Commit 목록 반환
  │    │    │
  │    │    ├─ 정렬된 객체 목록에서 ID 목록 추출
  │    │    └─ format_log(commits, sorted_hash)
  │    │
  │    └─ 정렬된 로그 문자열 반환
  │
  └─ 결과가 비어 있지 않으면 print(result)
```

작성자 정렬에서는 다음 부분만 달라진다.

```text
parse_sort_option("--sort-by=author")
  └─ "author"

get_sort_key(commit, "author")
  └─ commit.author
```

정렬 `LOG`는 기본 `LOG`의 `topological_order()`를 호출하지 않는다. 따라서 날짜·작성자 오름차순만 적용하며 부모 우선 조건은 별도로 적용하지 않는다.

---

## 7. PATH

입력 예시:

```text
path CI_2 CI_3
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("path CI_2 CI_3")
  │    └─ ["PATH", "CI_2", "CI_3"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ 저장소가 초기화됐는지 확인
  │    │
  │    ├─ find_shortest_path(commits, "CI_2", "CI_3")
  │    │    │
  │    │    ├─ 시작 ID와 도착 ID가 commits에 있는지 확인
  │    │    ├─ 두 ID가 같으면 ["CI_2"] 즉시 반환
  │    │    │
  │    │    ├─ build_distance_map(commits, "CI_3")
  │    │    │    │
  │    │    │    ├─ build_neighbors_map(commits)
  │    │    │    │    │
  │    │    │    │    ├─ build_children_map(commits)
  │    │    │    │    └─ 각 ID의 parents + children을 이웃 목록으로 구성
  │    │    │    │
  │    │    │    ├─ waiting = ["CI_3"]
  │    │    │    ├─ distance = {"CI_3": 0}
  │    │    │    ├─ BFS로 처음 발견한 이웃의 최소 거리 기록
  │    │    │    └─ 도착점에서 각 커밋까지의 거리 표 반환
  │    │    │
  │    │    ├─ 시작 ID가 거리 표에 없으면 None 반환
  │    │    │
  │    │    ├─ build_neighbors_map(commits)를 다시 호출
  │    │    │
  │    │    ├─ best_suffix = {도착 ID: 도착 ID}
  │    │    ├─ next_step = {}
  │    │    │
  │    │    ├─ 각 ID에서 거리가 정확히 1 작은 이웃만 후보로 확인
  │    │    ├─ "현재ID->남은경로" 전체 문자열을 비교
  │    │    ├─ 사전순으로 가장 작은 후보를 best_suffix에 저장
  │    │    ├─ 선택한 다음 이웃을 next_step에 저장
  │    │    │
  │    │    ├─ 시작 ID부터 next_step을 따라 실제 ID 목록 복원
  │    │    └─ 최단 경로 목록 반환
  │    │
  │    ├─ 반환값이 None이면 "No path" 반환
  │    └─ 경로가 있으면 "Path: " + " -> ".join(result) 반환
  │
  └─ print(result)
```

거리 계산을 도착점에서 시작하는 이유는 각 커밋에서 도착점까지 남은 거리를 알기 위해서다. 그 거리 값을 1씩 줄이는 이웃만 선택하면 최단 경로 길이를 유지하면서 사전순 동률 비교를 할 수 있다.

현재 구현에서는 `build_distance_map()` 내부에서 한 번, 경로 선택 전에 한 번 `build_neighbors_map()`을 호출한다.

---

## 8. ANCESTORS

입력 예시:

```text
ancestors CI_2
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("ancestors CI_2")
  │    └─ ["ANCESTORS", "CI_2"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ 저장소가 초기화됐는지 확인
  │    │
  │    ├─ find_ancestors(repository.commits, "CI_2")
  │    │    │
  │    │    ├─ 대상 ID가 commits에 있는지 확인
  │    │    ├─ start_commit = commits["CI_2"]
  │    │    ├─ parent_list = 시작 커밋의 직접 부모 목록
  │    │    ├─ parent_set = 지금까지 발견한 조상 ID 집합
  │    │    │
  │    │    ├─ parent_list가 빌 때까지 반복
  │    │    │    ├─ pop(0)으로 확인할 부모 ID를 꺼냄
  │    │    │    ├─ commits[parent]로 부모 Commit 객체 조회
  │    │    │    └─ 아직 발견하지 않은 부모의 부모를
  │    │    │         parent_list와 parent_set에 추가
  │    │    │
  │    │    └─ 모든 조상 ID 집합 반환
  │    │
  │    ├─ repository.commits의 ID를 저장 순서대로 순회
  │    ├─ ancestor_ids에 포함된 ID만 ordered_ids에 추가
  │    ├─ format_log(repository.commits, ordered_ids)
  │    └─ 조상 로그 문자열 반환
  │
  └─ 결과가 비어 있지 않으면 print(result)
```

`find_ancestors()`의 반환값은 중복이 없는 `set[str]`이다. CLI는 이 집합을 바로 출력하지 않고, 저장소의 커밋 저장 순서에 맞춰 ID 목록을 다시 만든 뒤 `format_log()`를 호출한다.

---

## 9. 키워드 SEARCH

입력 예시:

```text
search "login feature"
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line('search "login feature"')
  │    └─ ["SEARCH", "login feature"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ 저장소가 초기화됐는지 확인
  │    ├─ 검색 문자열이 비어 있는지 확인
  │    ├─ "--"로 시작하지 않으므로 키워드 검색 선택
  │    │
  │    ├─ Repository.search_by_keywords("login feature")
  │    │    │
  │    │    ├─ CommitIndex.find_by_keywords("login feature")
  │    │    │    │
  │    │    │    ├─ query.lower().split()
  │    │    │    │    └─ ["login", "feature"]
  │    │    │    │
  │    │    │    ├─ find_by_keyword("login")
  │    │    │    │    └─ keyword_index["login"]의 ID 집합
  │    │    │    │
  │    │    │    ├─ 첫 번째 후보 집합을 새 set으로 복사
  │    │    │    │
  │    │    │    ├─ find_by_keyword("feature")
  │    │    │    │    └─ keyword_index["feature"]의 ID 집합
  │    │    │    │
  │    │    │    ├─ 두 후보 집합의 교집합 계산
  │    │    │    └─ 모든 토큰을 가진 커밋 ID 집합 반환
  │    │    │
  │    │    ├─ 후보 ID마다 Repository.get_commit(id) 호출
  │    │    └─ 일치하는 Commit 객체 목록 반환
  │    │
  │    ├─ Commit 객체 목록에서 hash만 꺼내 ID 목록 생성
  │    ├─ format_log(repository.commits, commit_id_list)
  │    └─ 검색 결과 로그 문자열 반환
  │
  └─ 결과가 비어 있지 않으면 print(result)
```

여러 토큰은 OR가 아니라 AND로 처리한다. 따라서 `login`과 `feature` 두 색인에 모두 포함된 커밋만 반환한다. 토큰 순서나 메시지 안에서의 연속 여부는 검사하지 않는다.

---

## 10. 작성자 SEARCH

입력 예시:

```text
search --author="Alice Kim"
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line('search --author="Alice Kim"')
  │    └─ ["SEARCH", "--author=Alice Kim"]
  │
  ├─ execute_command(repository, parts)
  │    │
  │    ├─ validate_argument_count(parts)
  │    ├─ 저장소가 초기화됐는지 확인
  │    ├─ 검색 문자열이 비어 있는지 확인
  │    ├─ "--"로 시작하므로 작성자 옵션 검색 선택
  │    │
  │    ├─ parse_author_option("--author=Alice Kim")
  │    │    ├─ "--author=" 접두사인지 확인
  │    │    ├─ 이름이 비어 있는지 확인
  │    │    └─ "Alice Kim" 반환
  │    │
  │    ├─ Repository.search_by_author("Alice Kim")
  │    │    │
  │    │    ├─ CommitIndex.find_by_author("Alice Kim")
  │    │    │    ├─ author_index에 작성자가 없으면 빈 집합 반환
  │    │    │    └─ 있으면 연결된 커밋 ID 집합 반환
  │    │    │
  │    │    ├─ 후보 ID마다 Repository.get_commit(id) 호출
  │    │    └─ 일치하는 Commit 객체 목록 반환
  │    │
  │    ├─ Commit 객체 목록에서 hash만 꺼내 ID 목록 생성
  │    ├─ format_log(repository.commits, commit_id_list)
  │    └─ 검색 결과 로그 문자열 반환
  │
  └─ 결과가 비어 있지 않으면 print(result)
```

키워드 검색과 달리 작성자 이름에는 `lower()`를 적용하지 않는다. 따라서 `Alice Kim`과 `alice kim`은 서로 다른 작성자로 검색된다.

---

## 11. EXIT와 QUIT

입력 예시:

```text
exit
quit
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("exit")
  │    └─ ["EXIT"]
  │
  ├─ parts[0]이 EXIT 또는 QUIT인지 확인
  ├─ validate_argument_count(parts)
  │    └─ 종료 명령에 인자가 없는지 확인
  │
  └─ break
       └─ while 반복 종료 → run_repl() 종료 → 프로그램 종료
```

`EXIT`와 `QUIT`은 `execute_command()`로 전달되지 않는다. `run_repl()`이 두 명령을 먼저 확인해서 직접 반복문을 끝낸다. 종료하면 인메모리 `Repository`의 모든 상태도 사라진다.

---

## 12. 빈 입력

입력 예시:

```text
mini-git>
```

호출 흐름:

```text
main.py: run_repl()
  │
  ├─ parse_command_line("")
  │    ├─ shlex.split("")
  │    └─ [] 반환
  │
  ├─ parts == [] 확인
  └─ continue
       └─ 아무 기능도 호출하거나 출력하지 않고 다음 프롬프트 표시
```

---

## 13. 오류가 발생했을 때의 공통 흐름

예상된 입력 오류는 각 함수에서 `ValueError`로 전달되고 `run_repl()`에서 한 번에 처리한다.

```text
main.py: run_repl()
  │
  └─ try
       │
       ├─ parse_command_line()
       ├─ validate_argument_count()
       ├─ parse_author_option() 또는 parse_sort_option()
       ├─ Repository의 상태 변경·조회 메서드
       └─ graph.py의 탐색 함수
            │
            └─ 어느 단계에서든 ValueError 발생 가능
                 │
                 ▼
            except ValueError as e
                 ├─ print(f"[오류] {e}")
                 └─ 다음 while 반복으로 이동
```

대표적인 오류 발생 위치:

| 입력 문제 | 오류를 발견하는 곳 |
| --- | --- |
| 닫히지 않은 따옴표 | `shlex.split()` |
| 알 수 없는 명령 | `validate_argument_count()` |
| 인자 누락 또는 초과 | `validate_argument_count()` |
| 빈 사용자명·브랜치명·메시지·검색어 | `execute_command()`의 명령별 검사 |
| 잘못된 `--author` 형식 | `parse_author_option()` |
| 잘못된 `--sort-by` 값 | `parse_sort_option()` |
| 초기화 전 저장소 명령 | `Repository` 메서드 또는 `execute_command()` |
| 중복 브랜치·없는 브랜치 | `Repository.create_branch()`·`switch_branch()` |
| 없는 커밋으로 PATH·ANCESTORS 실행 | `find_shortest_path()`·`find_ancestors()` |

오류가 발생하면 해당 명령의 결과 문자열은 만들어지지 않는다. 하지만 같은 `Repository` 객체와 이미 성공한 이전 상태는 유지되며, REPL은 다음 입력을 계속 받는다.

---

## 14. 명령과 핵심 함수 대응표

| 명령 | 중심 함수 | 직접 사용하는 하위 기능 |
| --- | --- | --- |
| `INIT` | `Repository.initialize()` | 저장소 초기 상태 설정 |
| `BRANCH` | `Repository.create_branch()` | 현재 브랜치 끝 ID 복사 |
| `SWITCH` | `Repository.switch_branch()` | `head` 변경 |
| `COMMIT` | `Repository.create_commit()` | ID 생성, `Commit` 생성, 저장, 브랜치 이동, 색인 갱신 |
| `LOG` | `topological_order()` | 자식 표, 부모 수 표, Kahn 방식 순서 구성 |
| `LOG --sort-by=...` | `format_sorted_log()` | 옵션 파싱, 삽입 정렬, 정렬 키 선택 |
| `PATH` | `find_shortest_path()` | 무방향 이웃 표, BFS 거리, 사전순 동률 선택, 경로 복원 |
| `ANCESTORS` | `find_ancestors()` | 부모 방향 BFS, 중복 방지 집합 |
| `SEARCH <keyword>` | `Repository.search_by_keywords()` | 키워드 역색인과 집합 교집합 |
| `SEARCH --author=...` | `Repository.search_by_author()` | 작성자 역색인 |
| `EXIT`·`QUIT` | `run_repl()` | 인자 검증 후 반복 종료 |

`format_log()`는 기본 `LOG`, 정렬 `LOG`, `ANCESTORS`, 두 종류의 `SEARCH`가 공통으로 사용하는 최종 출력 함수다. 반면 `PATH`는 커밋 상세 로그가 아니라 ID 연결 문자열을 직접 만든다.
