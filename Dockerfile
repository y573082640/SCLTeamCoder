FROM python:3.9.7-slim

WORKDIR /app
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple some-package

EXPOSE 8000

CMD ["python", "app.py"]