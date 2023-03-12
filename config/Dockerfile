FROM python:3.9

RUN pip install --upgrade pip

WORKDIR /app

COPY . .

RUN pip install -r ./config/requirements.txt

ENTRYPOINT python3 -u ./src/main.py