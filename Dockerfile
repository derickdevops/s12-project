FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["app.py"]
