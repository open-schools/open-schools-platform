# This docker file is used for production
# Creating image based on official python3 image
FROM python:3.10

# Installing all python dependencies
ADD requirements/ requirements/
RUN pip install -r requirements/base.txt

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
ENTRYPOINT ["bin/sh", "docker/web_entrypoint.sh", "production.py"]
