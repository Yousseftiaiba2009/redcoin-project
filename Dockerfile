FROM alpine:latest
RUN apk add --no-cache wget
RUN wget https://github.com/monero-project/monero/releases/download/v0.18.3.3/monero-linux-x64-v0.18.3.3.tar.bz2
RUN tar -xvjf monero-linux-x64-v0.18.3.3.tar.bz2
WORKDIR /monero-v0.18.3.3
