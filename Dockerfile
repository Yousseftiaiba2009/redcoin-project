FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install flask flask-cors gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
