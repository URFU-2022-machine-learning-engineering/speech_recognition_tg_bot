FROM python:3.10
LABEL authors="Alexandr Orlov, Vladimir Katin"

WORKDIR /bot

COPY main.py requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
