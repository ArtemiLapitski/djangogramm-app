ARG TARGET_PLATFORM='linux/amd64'

FROM --platform=${TARGET_PLATFORM} python:3.9

COPY . .

RUN pip install -r requirements.txt

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]
