# using the official ubuntu base image 
FROM ubuntu:latest 

ARG GO_VERSION
ENV GO_VERSION=1.24.5

# installing make, git, gcc
RUN apt-get update && apt-get install -y make git curl tar python3-pip
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get -y install build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \ 
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        libsqlite3-dev \
        libbz2-dev \
        wget

# Install Python
RUN cd /usr/src \
    && wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz \
    && tar -xzf Python-3.11.9.tgz \
    && cd Python-3.11.9 \
    && ./configure --enable-optimizations \
    && make altinstall
    
# Install Golang
RUN wget -P /tmp "https://dl.google.com/go/go${GO_VERSION}.linux-amd64.tar.gz"
RUN tar -C /usr/local -xzf "/tmp/go${GO_VERSION}.linux-amd64.tar.gz"
RUN rm "/tmp/go${GO_VERSION}.linux-amd64.tar.gz"

ENV GOPATH=/go
ENV PATH=$GOPATH/bin:/usr/local/go/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

RUN go install golang.org/x/tools/gopls@latest

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt --break-system-packages

# specifying the command to run when the container starts
CMD ["/bin/bash"]