FROM python:3.8
WORKDIR /code
RUN apt-get update && apt-get install -y libsndfile1-dev
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src .
ENV PYTHONUNBUFFERED=True
