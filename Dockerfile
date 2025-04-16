# Dockerfile

# Python 기반 이미지 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY ./requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 소스 복사
COPY . .

# 환경 변수 설정 (timezone 문제 예방)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 기본 실행 명령어 (개발용)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]