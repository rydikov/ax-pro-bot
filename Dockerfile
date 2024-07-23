FROM python:3.12.2-slim

ENV PYTHONDONTWRITEBYTECODE yes

RUN apt-get update
RUN apt-get install -y git

WORKDIR /app

RUN git clone https://github.com/rydikov/ax-pro.git

COPY bot.py bot.py
COPY requires.txt requires.txt

RUN pip install -r requires.txt

RUN pip install -e ax-pro
