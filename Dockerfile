FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py migrate

CMD gunicorn jee_chatbot.wsgi:application --bind 0.0.0.0:8001
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
