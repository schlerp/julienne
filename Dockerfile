FROM --platform=arm64 ubuntu:latest

ENV TZ=Etc/UTC

# set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# make apt only install what we ask for explicitly
RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker \
    && echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker

# install python
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update \
    && apt-get install -y \
    python3-venv \
    python3-pip \
    python3 \
    python-is-python3 \
    curl

RUN python3 -m pip install poetry

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN cd /app && poetry export -f requirements.txt --output requirements.txt && pip install -r /app/requirements.txt
