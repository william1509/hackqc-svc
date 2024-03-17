FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip

EXPOSE 5000
COPY . /src
WORKDIR /src
RUN pip3 install -r requirements.txt


CMD [ "python3", "src"]