FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY exporter/main.py ./exporter.py
COPY data/systems.json.gz ./data/systems.json.gz

EXPOSE 8000

CMD [ "python", "./exporter.py" ]
