FROM python:3.7-slim
RUN apt-get update && apt-get install make && rm -fr /var/lib/apt/lists/*

WORKDIR /work

COPY requirements.txt /work/
COPY tests/requirements.txt /work/tests/
COPY docs/requirements.txt /work/docs/
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir \
    async-timeout>=3.0.0 \
    aioredis>=1.1.0 \
    click>=6.7 \
    pydantic>=0.20 \
    dataclasses>=0.6 \
    watchgod>=0.4
