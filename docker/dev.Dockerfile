# This docker file is used for local development via docker-compose
# Creating image based on official python3 image
FROM python:3.10

# Fix python printing
ENV PYTHONUNBUFFERED 1

# Installing all python dependencies
ADD requirements/ requirements/
RUN pip install -r requirements/dev.txt

# GeoDjango dependencies
RUN apt-get update -y \
    && apt-get install binutils libproj-dev gdal-bin -y \
    && apt-get install libgeos++ -y \
    && apt-get install proj-bin -y \
    && apt install gdal-bin -y

# Get the django project into the docker container
WORKDIR /app
ADD ./ /app/

# Use gunicorn
RUN chmod a+x docker/web_entrypoint.sh
ENTRYPOINT ["/bin/bash", "docker/web_entrypoint.sh", "dev.py"]