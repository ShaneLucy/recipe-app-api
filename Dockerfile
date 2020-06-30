#the docker image this is based on
FROM python:3.7-alpine

#reccomended to run python in ubuffered mode in docker
ENV PYTHONUNBUFFERED 1

#storing dependencies 
COPY ./requirements.txt /requirements.txt

#installs dependencies
RUN pip install -r /requirements.txt

# creates directory in docker image
RUN mkdir /app
#makes this directory the working directory
WORKDIR /app
#copies app folder from local machine into docker image
COPY ./app /app

#create user to run application using docker so application won't be run as root
RUN adduser -D user
#switch to user
USER user

