FROM python:3-bullseye

COPY config.json /config.json
COPY run.py /run.py
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

EXPOSE 104
CMD ["python", "run.py"]
