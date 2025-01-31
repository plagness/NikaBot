FROM python:3.9-alpine

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apk --no-cache add ffmpeg

WORKDIR /bot
COPY . /bot
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]