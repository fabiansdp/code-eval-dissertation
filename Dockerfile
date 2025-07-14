# using the official ubuntu base image 
FROM ubuntu:latest 

# installing make, git, gcc
RUN apt-get update && apt-get install -y make git curl tar
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

RUN cd /usr/src \
    && wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz \
    && tar -xzf Python-3.11.9.tgz \
    && cd Python-3.11.9 \
    && ./configure --enable-optimizations \
    && make altinstall
# Download and extract CodeQL
# RUN curl -L https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.22.1/codeql-bundle-linux64.tar.gz | tar -xz -C /opt/ && \
#     ln -s /opt/codeql /usr/local/bin/codeql

# Set PATH (optional if you're using the symlink)
# ENV PATH="/opt/codeql:$PATH"

WORKDIR /app


COPY requirements.txt /app

RUN pip install -r requirements.txt --break-system-packages

# specifying the command to run when the container starts
CMD ["/bin/bash"]