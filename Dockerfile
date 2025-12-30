FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y wget bzip2 ca-certificates
RUN wget https://downloads.getmonero.org/cli/monero-linux-x64-v0.18.3.3.tar.bz2
RUN tar -xvjf monero-linux-x64-v0.18.3.3.tar.bz2
RUN cp monero-x86_64-linux-gnu-v0.18.3.3/monerod /usr/local/bin/monerod
RUN chmod +x /usr/local/bin/monerod
WORKDIR /usr/local/bin
# هذا السطر هو الذي سيجعل التعدين يبدأ تلقائياً
ENTRYPOINT ["monerod"]
