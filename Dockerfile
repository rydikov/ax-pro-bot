FROM python:3.12.2-slim

ENV PYTHONDONTWRITEBYTECODE yes

RUN apt-get update
RUN apt-get install -y git

WORKDIR /app

COPY bot.py bot.py
COPY requires.txt requires.txt

RUN pip install -r requires.txt

RUN pip install -e git+https://github.com/rydikov/ax-pro.git@52ed273304a784d8bab5664ce8bd540b4bdddb9c#egg=axpro
