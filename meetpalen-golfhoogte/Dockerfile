ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.20
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

# Install Python from APK, create venv, install deps
ARG BUILD_NO_CACHE=0
RUN apk add --no-cache python3 py3-virtualenv py3-pip
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir -r /tmp/requirements.txt

ENV PATH="/venv/bin:$PATH"

# Copy application
COPY app /app

# Copy root filesystem
COPY rootfs /

RUN chmod a+x /run.sh

CMD ["/run.sh"]
