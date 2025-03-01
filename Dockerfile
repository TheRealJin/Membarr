FROM python:3.9.1-alpine

# Add Alpine edge/testing repositories
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
    echo "http://dl-8.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# Install dependencies
RUN apk --no-cache add \
    git \
    cloc \
    openssl \
    openssl-dev \
    openssh \
    alpine-sdk \
    bash \
    gettext \
    sudo \
    build-base \
    gnupg \
    linux-headers \
    xz

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command
CMD ["python", "-u", "run.py"]
