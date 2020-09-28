# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /app/

RUN apt -qq update
RUN apt -qq install -y --no-install-recommends \
        ffmpeg

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .

ENV ENV true

# command to run on container start
CMD [ "python", "-m", "mega" ]