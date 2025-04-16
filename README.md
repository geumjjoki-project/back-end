# 금쪼기 (Geumjjoki) 백엔드

금쪼기 프로젝트 백엔드 리포지토리입니다.

## 기술 스택

- **프레임워크**: Django (Python)
- **데이터베이스**: MySQL 8.0
- **컨테이너화**: Docker, Docker Compose

## 개발 환경 설정

### 사전 요구사항

- Docker 및 Docker Compose 설치
- Git

### 설치 및 실행 방법

1. 리포지토리 클론
   ```bash
   git clone <repository-url>
   cd geumjjoki-back-end
   ```

2. Docker Compose로 실행
   ```bash
   # 컨테이너 빌드 및 백그라운드 실행
   docker-compose up -d
   
   # 로그 확인
   docker-compose logs -f
   ```

3. 서비스 접근
   - **Django 애플리케이션**: http://localhost:8000
   - **Adminer (DB 관리)**: http://localhost:8080

## 데이터베이스 정보

- **호스트**: localhost (외부 접속) / db (컨테이너 내부 접속)
- **포트**: 3306
- **데이터베이스 이름**: geumjjoki_database
- **사용자**: geumjjoki_user
- **비밀번호**: 1234

### Adminer 접속 정보
- **시스템**: MySQL
- **서버**: db
- **사용자**: geumjjoki_user
- **비밀번호**: 1234
- **데이터베이스**: geumjjoki_database

## 개발 작업 시 참고사항

### 컨테이너 관리 명령어

```bash
# 모든 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose stop

# 컨테이너 삭제 (볼륨 유지)
docker-compose down

# 컨테이너 및 볼륨 삭제 (모든 데이터 초기화)
docker-compose down -v

# 로그 확인
docker-compose logs -f
```

### 컨테이너 내부 진입

```bash
# Django 애플리케이션 컨테이너 진입
docker exec -it geumjjoki_app bash

# MySQL 데이터베이스 컨테이너 진입
docker exec -it geumjjoki_db bash

# MySQL CLI 직접 접속
docker exec -it geumjjoki_db mysql -u geumjjoki_user -p
```

### Django 명령어 실행 (컨테이너 내부에서)

```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 슈퍼유저 생성
python manage.py createsuperuser
```

### 외부에서 컨테이너의 Django 명령어 실행

```bash
# 마이그레이션 생성
docker exec -it geumjjoki_app python manage.py makemigrations

# 마이그레이션 적용
docker exec -it geumjjoki_app python manage.py migrate

# 슈퍼유저 생성
docker exec -it geumjjoki_app python manage.py createsuperuser
```

### 코드 변경 적용

- 대부분의 코드 변경은 볼륨 마운트로 인해 자동으로 컨테이너에 반영됩니다
- Django 앱 추가 또는 모델 변경 후에는 마이그레이션 명령을 실행해야 합니다
- requirements.txt 또는 Dockerfile 변경 시에는 컨테이너를 재빌드해야 합니다:
  ```bash
  docker-compose down
  docker-compose up --build -d
  ```

## 외부 GUI 툴로 데이터베이스 접근

다음 GUI 도구를 사용하여 MySQL 데이터베이스에 접근할 수 있습니다:
- MySQL Workbench
- DBeaver
- TablePlus
- HeidiSQL

접속 정보:
- 호스트: localhost 또는 127.0.0.1
- 포트: 3306
- 사용자: geumjjoki_user
- 비밀번호: 1234
- 데이터베이스: geumjjoki_database

## Commit Message
```plane
<type>: <subject>

<body>

<footer>

## Type
feat : 새로운 기능 추가, 기존의 기능을 요구 사항에 맞추어 수정
fix : 기능에 대한 버그 수정
build : 빌드 관련 수정
chore : 패키지 매니저 수정, 그 외 기타 수정 ex) .gitignore
ci : CI 관련 설정 수정
docs : 문서(주석) 수정
style : 코드 스타일, 포맷팅에 대한 수정
refactor : 기능의 변화가 아닌 코드 리팩터링 ex) 변수 이름 변경
test : 테스트 코드 추가/수정
release : 버전 릴리즈

## Subject
Type 과 함께 헤더를 구성합니다. 예를들어, 로그인 API 를 추가했다면 다음과 같이 구성할 수 있습니다.

ex) feat: Add login api

## Body
헤더로 표현이 가능하다면 생략이 가능합니다. 아닌 경우에는 자세한 내용을 함께 적어 본문을 구성합니다.

## Footer
어떠한 이슈에 대한 commit 인지 issue number 를 포함합니다. 위의 좋은 예시에서는 (#1) 처럼 포함시켰습니다. 그리고 close #1 처럼 close 를 통해 해당 이슈를 닫는 방법도 있습니다.
```
