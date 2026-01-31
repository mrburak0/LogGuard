FROM python:3.9-slim
WORKDIR /app
COPY . .

COPY test.log /var/log/test.log 

VOLUME ["/var/log"]
CMD ["python", "log_guard.py"]