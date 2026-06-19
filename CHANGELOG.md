
## 2026-06-19 - 500 Error Hotfix

- `DEBUG=False` 또는 Render 배포 환경에서 `sound/beep.mp3` static manifest 누락으로 500이 발생할 수 있는 문제를 수정했습니다.
- staticfiles backend를 `CompressedManifestStaticFilesStorage`에서 `CompressedStaticFilesStorage`로 변경했습니다.
- `WHITENOISE_MANIFEST_STRICT = False`를 추가했습니다.
- `Procfile`에 `collectstatic --noinput`, `migrate`, `ensure_profiles` 실행을 추가했습니다.

# 변경 이력

## 2026-06-19 수정본

### 수정

- 위치코드 검색 파싱 로직 개선
  - `B0F21`을 `B / 0F / 2 / 1`로 정확히 해석
  - 숫자 열(`2`, `10`, `13`) 지원
  - QR 형식 `B/0F/2/1` 지원
  - 선반 전체 검색 `B0F` 지원
- 권한 체크 보강
  - 삭제: `GRADE3`만 가능
  - CSV 업로드: `GRADE3`만 가능
  - CSV 다운로드: `GRADE2`, `GRADE3` 가능
  - 위치코드 검색: 로그인 사용자만 가능
- CSV 업로드 검증 강화
  - 헤더 검증
  - UTF-8 BOM 대응
  - 빈 행 제외
  - 컬럼 수 오류 표시
  - 빈 값 오류 표시
- 검색 결과 페이지네이션 추가
  - 100개 단위 표시
- 삭제 후 검색/위치 화면 유지
- 사용자 Profile 자동 생성 signal 수정
- 기존 사용자 Profile 보정 management command 추가
- Django settings 정리
  - 환경변수 기반 설정
  - SQLite 기본값
  - PostgreSQL/DATABASE_URL 선택 지원
  - 로컬 HTTP 환경에서 Secure 쿠키로 인한 로그인 문제 완화
- README, PROJECT_OVERVIEW, TODO, .gitignore, .env.example 추가/보강

### 보류

운영 데이터 영향이 큰 아래 항목은 코드에는 즉시 반영하지 않고 TODO로 분리했습니다.

- 제품/위치/재고/이동로그 모델 분리
- 박스 수량 필드 추가
- 삭제 대신 비활성화 처리
- 위치 이동 이력
- QR 라벨 출력

## 2026-06-19 로그인 후 500 핫픽스
- 기존 사용자에게 `Profile` 행이 없을 때 로그인 직후 `user.profile.grade` 접근으로 500이 나는 문제를 방지했습니다.
- 템플릿에서 `user.profile.grade`를 직접 읽지 않고 `user_grade` 컨텍스트 값을 사용하도록 변경했습니다.
- 권한 데코레이터가 누락된 Profile을 자동 보정하도록 변경했습니다.
- `python manage.py check` 및 Profile 누락 사용자 로그인 후 홈 화면 접근을 확인했습니다.
