# 베이스 이미지 (본인 프로젝트에 맞는 버전 기입)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/bbang"

# 종속성 파일 복사
COPY ./poetry.lock /bbang/
COPY ./pyproject.toml /bbang/

# 작업 디렉토리 설정
WORKDIR /bbang

# 종속성 설치
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN python -m pip install --upgrade pip
RUN poetry install
RUN poetry add gunicorn

# 애플리케이션 코드 복사
COPY . /bbang
WORKDIR /bbang/app


# 소켓 파일 생성 디렉토리 권한 설정
RUN mkdir -p /bbang && chmod -R 755 /bbang


COPY ./scripts /scripts
RUN chmod +x /scripts/run.sh
CMD ["/scripts/run.sh"]