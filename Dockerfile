# using the official ubuntu base image 
FROM ubuntu:latest 

# installing make, git, gcc
RUN apt-get update && apt-get install -y make git curl tar

RUN apt-get install -y python3

RUN apt-get install -y python3-pip

# Download and extract CodeQL
RUN curl -L https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.22.1/codeql-bundle-linux64.tar.gz | tar -xz -C /opt/ && \
    ln -s /opt/codeql /usr/local/bin/codeql

# Set PATH (optional if you're using the symlink)
ENV PATH="/opt/codeql:$PATH"

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt --break-system-packages

# specifying the command to run when the container starts
CMD ["/bin/bash"]