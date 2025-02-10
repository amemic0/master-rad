
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY intersection2.py /app/
CMD ["python", "intersection2.py"]