FROM python:3.12-alpine


WORKDIR /app


RUN apk add --no-cache curl ca-certificates


# install cloudflared (auto-arch)

RUN ARCH=$(uname -m) && \

    if [ "$ARCH" = "x86_64" ]; then CF_ARCH=amd64; \

    elif [ "$ARCH" = "aarch64" ]; then CF_ARCH=arm64; \

    else echo "Unsupported arch"; exit 1; fi && \

    curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$CF_ARCH \

      -o /usr/local/bin/cloudflared && \

    chmod +x /usr/local/bin/cloudflared


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY bot.py .


CMD ["python", "bot.py"]

