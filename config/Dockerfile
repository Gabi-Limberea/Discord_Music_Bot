FROM python:3.9
RUN pip install --upgrade pip
WORKDIR /app
COPY ./config/requirements.txt .
RUN pip install -r requirements.txt
COPY ../src .
ENV BOT_TOKEN = $BOT_TOKEN
ENTRYPOINT python main.py