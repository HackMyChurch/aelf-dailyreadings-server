FROM alpine:3.18.4
MAINTAINER Jean-Tiare Le Bigot <support@epitre.co>

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache python3 python3-dev py3-lxml gcc g++ hunspell hunspell-dev
RUN python3 -m ensurepip && pip3 install --no-cache --upgrade pip setuptools wheel
RUN ln -s /usr/lib/libhunspell-1.7.so /usr/lib/libhunspell.so

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

USER nobody
CMD ["python3", "start-production-server.py"]
