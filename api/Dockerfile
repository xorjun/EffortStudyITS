FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

#ENV ITS_ENV=production

RUN apt-get update \
    && apt-get clean

RUN pip install -r /app/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /app/

#CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
#CMD ["python", "main.py"]
