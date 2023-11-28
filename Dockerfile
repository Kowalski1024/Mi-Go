FROM nvidia/cuda:12.0.0-base-ubuntu20.04
FROM python:3.10

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y --quiet=2

COPY . .

RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

# Whisper
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ffmpeg
RUN apt-get -y install git
RUN pip install git+https://github.com/openai/whisper.git

ENTRYPOINT [ "/bin/bash" ]

