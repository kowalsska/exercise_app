FROM python:3.8

WORKDIR /exercise-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./app/main_app.py"]