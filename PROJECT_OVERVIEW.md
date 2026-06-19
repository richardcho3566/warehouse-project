# Warehouse Project 개요

## 목적

사내 제품 위치 조회 및 창고 위치 관리를 위한 Django 기반 웹앱입니다. 제품명 또는 위치코드로 제품 위치를 조회하고, 권한 등급에 따라 제품 등록, CSV 업로드/다운로드, 사용자 등급 관리 기능을 제공합니다.

## 현재 주요 기능

- 로그인 / 로그아웃 / 회원가입
- 사용자 등급 관리
  - `GRADE1`: 조회 중심
  - `GRADE2`: 조회, 제품 등록, CSV 다운로드
  - `GRADE3`: 관리자, CSV 업로드, 삭제, 회원 등급 관리
- 제품명 검색
- 위치코드 검색
- QR 스캔 입력
- 제품 위치 등록
- CSV 업로드 / 다운로드
- 첫 화면 전체 목록 자동 로딩 방지
- 검색 결과 100개 단위 페이지네이션

## 위치코드 규칙

현재 위치코드는 다음 구조를 기준으로 파싱합니다.

```text
B0F21 = B창고 / 0F선반 / 2열 / 1층
B0F101 = B창고 / 0F선반 / 10열 / 1층
B0F = B창고 / 0F선반 전체
```

지원 입력 형식:

```text
B0F21
B-0F-21
B/0F/2/1
B0F
```

## 폴더 구조

```text
warehouse-project
├─ manage.py
├─ requirements.txt
├─ README.md
├─ PROJECT_OVERVIEW.md
├─ TODO.md
├─ .env.example
├─ .gitignore
├─ inventory/
│  ├─ models.py
│  ├─ views.py
│  ├─ forms.py
│  ├─ urls.py
│  ├─ utils.py
│  ├─ decorators.py
│  ├─ signals.py
│  ├─ templates/
│  ├─ static/
│  └─ management/commands/ensure_profiles.py
└─ warehouse_project/
   ├─ settings.py
   ├─ urls.py
   ├─ asgi.py
   └─ wsgi.py
```

## 운영상 주의사항

- 실제 운영 DB 파일(`db.sqlite3`)은 Git에 올리지 않는 것을 권장합니다.
- `.env` 파일에 비밀번호, Secret Key, DB 접속 정보를 저장하고 Git에는 올리지 않습니다.
- 사내망에서 인터넷이 불안정하면 Bootstrap, html5-qrcode CDN을 로컬 static 파일로 교체하는 것이 좋습니다.
- 사용자 등급 화면에 들어가기 전 기존 사용자에게 `Profile`이 없으면 아래 명령으로 보정할 수 있습니다.

```bash
python manage.py ensure_profiles
```

## 다음 확장 방향

- 위치 이동 이력
- 작업 로그
- 빈 위치 조회
- 위치별 적재율 표시
- QR 위치 라벨 출력
- Excel 업로드/다운로드
- 제품 마스터 / 위치 마스터 / 재고 위치 / 이동 로그 모델 분리
