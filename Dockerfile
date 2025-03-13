# 베이스 이미지 (본인 프로젝트에 맞는 버전 기입)
FROM python:3.12-2

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 종속성 파일 복사
COPY ./poetry.lock /mini_project/
COPY ./pyproject.toml /mini_project/

# 작업 디렉토리 설정
WORKDIR /mini_project

# 종속성 설치
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN poetry add gunicorn

# 애플리케이션 코드 복사
COPY ./app /mini_project/app
WORKDIR /mini_project/app


# 소켓 파일 생성 디렉토리 권한 설정
RUN mkdir -p /mini_project && chmod -R 755 /mini_project

# 변경된 코드: 스크립트를 사용하여 애플리케이션 실행
COPY ./scripts /scripts
RUN chmod +x /scripts/run.sh
CMD ["/scripts/run.sh"]