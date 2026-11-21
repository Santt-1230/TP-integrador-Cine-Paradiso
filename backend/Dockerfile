
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers", "3", "--threads", "2", "--timeout", "60", \
     "--access-logfile", "-", "--access-logformat", "%(r)s %(s)s %(L)ss", \
     "-b", "0.0.0.0:5000", "app:app"]
