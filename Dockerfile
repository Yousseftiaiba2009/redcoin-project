FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y wget bzip2
RUN wget https://downloads.getmonero.org/cli/monero-linux-x64-v0.18.3.3.tar.bz2
RUN tar -xvjf monero-linux-x64-v0.18.3.3.tar.bz2
RUN mv monero-x86_64-linux-gnu-v0.18.3.3/* /usr/local/bin/
WORKDIR /usr/local/bin
