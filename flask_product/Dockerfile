
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /flask_product

COPY requirements.txt /flask_product/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /flask_product/

RUN pip install celery

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
