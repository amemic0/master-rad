FROM python:3.10-slim

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

COPY server2.py /app

EXPOSE 8080

CMD ["python", "server2.py"]
