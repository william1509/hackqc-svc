FROM ubuntu:22.04
RUN apt-get upgrade
RUN apt-get install -y python

EXPOSE 5000
COPY . /src

WORKDIR /src
RUN pip install -r /src/requirements.txt


CMD [ "python3", "src"]