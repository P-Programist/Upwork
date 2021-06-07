FROM python:3.9
COPY . /bot
COPY requirements.txt /bot
WORKDIR /bot

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install redis-server -y
RUN apt-get install --no-install-recommends -y gcc
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install -r /bot/requirements.txt

CMD ["python3", "/bot/main.py"]