# set base image (host OS)
FROM python:3.8

# set the working directory in the container to /src
WORKDIR src

# copy and install dependencies file to working directory
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy the config file to working directory
COPY .env .

# copy the content of the local src directory to the working directory
COPY ./src /src

ENTRYPOINT ["python"]
CMD ["main.py"]
