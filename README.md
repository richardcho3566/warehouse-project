# Warehouse Project

사내 제품 위치 조회 및 창고 위치 관리를 위한 Django 웹앱입니다.

## 주요 기능

- 제품명 검색
- 위치코드 검색
- QR 스캔 입력
- 제품 위치 등록
- CSV 업로드 / 다운로드
- 로그인 / 회원가입
- 사용자 등급 관리
- 검색 결과 페이지네이션

## 사용자 등급

| 등급 | 권한 |
|---|---|
| GRADE1 | 제품/위치 조회 |
| GRADE2 | 조회, 제품 등록, CSV 다운로드 |
| GRADE3 | 관리자, CSV 업로드, 삭제, 회원 등급 관리 |

## 위치코드 검색

지원 예시:

```text
B0F21     = B창고 / 0F선반 / 2열 / 1층
B0F101    = B창고 / 0F선반 / 10열 / 1층
B-0F-21   = B창고 / 0F선반 / 2열 / 1층
B/0F/2/1  = B창고 / 0F선반 / 2열 / 1층
B0F       = B창고 / 0F선반 전체
```

## 설치

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 환경 설정

`.env.example`을 참고해 `.env`를 만들 수 있습니다. 현재 설정은 기본적으로 SQLite를 사용합니다.

### SQLite 기본 실행

```bash
python manage.py migrate
python manage.py ensure_profiles
python manage.py runserver
```

### PostgreSQL 사용 시

환경변수 예시:

```text
DB_ENGINE=postgresql
DB_NAME=warehouse_project
DB_USER=postgres
DB_PASSWORD=비밀번호
DB_HOST=localhost
DB_PORT=5432
```

또는 `DATABASE_URL`을 사용할 수 있습니다.

## CSV 업로드 형식

CSV 파일 첫 줄은 반드시 아래 순서여야 합니다.

```csv
product_name,warehouse,shelf_number,column,level
```

예시:

```csv
product_name,warehouse,shelf_number,column,level
ABC-01*316,B,0F,2,1
ABC-02*316,B,0F,10,1
```

## Git 관리 권장사항

아래 파일은 Git에 올리지 않는 것을 권장합니다.

```text
db.sqlite3
.env
__pycache__/
*.pyc
staticfiles/
media/
*.log
```

## 문서

- `PROJECT_OVERVIEW.md`: 프로젝트 구조와 운영 설명
- `TODO.md`: 향후 개선/업그레이드 목록
- `CHANGELOG.md`: 변경 이력
