FROM python:3.11-slim
ENV APP_HOME=/app
WORKDIR $APP_HOME
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["python", "main.py"]