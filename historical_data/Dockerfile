FROM python:3.9-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install pandas numpy pymongo

CMD ["python", "./generation.py"]
