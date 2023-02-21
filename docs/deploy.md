# Deploy [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

1. Run db
```
docker-compose up db
```
2. Create virtualenv
```
python -m venv [path to venv folder]
```
3. Activate virtualenv
```
source [path to venv folder]/Scripts/activate
```
4. Install requirements. Don't forget to change production.txt to local.txt in requirements.txt if it's necessary!
```
pip install -r requirements/local.txt
```
> For MacOS developer: change string "psycopg2" to "psycopg2-binary" in requirements/base.txt

5. Create .env file with 
```
DATABASE_URL=postgres://postgres:postgres@localhost:5432/local_db
```
6. In created .env file define next variables:
- firebase api key ```GOOGLE_API_KEY=<key>```
- google maps api key ```GOOGLE_MAPS_API_KEY=<key>```
- object storage access key ```AWS_ACCESS_KEY=<key>```
- object storage secret access key ```AWS_SECRET_ACCESS_KEY=<key>```
- object storage bucket name ```YANDEX_CLIENT_DOCS_BUCKET_NAME=<key>```
- ⚠️email id ```EMAIL_ID=<key>```
- ⚠️mail.ru api key ```EMAIL_PRIVATE_API_KEY=<key>```
- firebase cloud messaging server key ```FCM_SERVER_KEY=<key>```
- ```FIREBASE_PROJECT_ID=<id>```
- ```FIREBASE_PRIVATE_KEY_ID=<id>```
- ```FIREBASE_PRIVATE_KEY=<key>```
- ```FIREBASE_CLIENT_EMAIL=<email>```
- ```FIREBASE_CLIENT_ID=<id>```
- ```FIREBASE_CLIENT_CERT_URL=<url>```
7. Migrate
```
python manage.py migrate
```
8. Collect static
```
python manage.py collectstatic
```
9. Run django server
```
python manage.py runserver [port]
```
10. Install pre-commit hooks
```
pre-commit install
```
11. Install pre-push hooks
```
pre-commit install --hook-type pre-push
```
12. Install GeoDjango packages

> You can specify custom paths to GeoDjango packages in .env file like this.
> Special instructions for specifying these paths are provided for each system.
- Paths to GDAL and geos
```
GEO_DJANGO_CUSTOM_PATHS=True
GDAL_LIBRARY_PATH=<path-to-file>
GEOS_LIBRARY_PATH=<path-to-file>
```
- Paths to OSGEO4W_ROOT, GDAL_DATA and PROJ_LIB
```
GEO_DJANGO_CUSTOM_ENV_VARIABLES=True
OSGEO4W_ROOT=<path-to-file>
GDAL_DATA=<path-to-file>
PROJ_LIB=<path-to-file>
```

# GeoDjango packages installation for windows

1. Download GDAL‑3.2.3‑cp39‑cp39‑win_amd64.whl from https://www.lfd.uci.edu/~gohlke/pythonlibs/

2. Install GDAL
```
pip install <path-to-GDAL‑3.2.3‑cp39‑cp39‑win_amd64.whl>
```
> If django has troubles with finding GDAL or geos, you need to write below line in .env file
```
GEO_DJANGO_CUSTOM_PATHS=True
```

# GeoDjango packages installation for linux

1. Run `apt-get update`

2. Run `[sudo] apt-get install binutils libproj-dev gdal-bin`

3. Install geos
```
[sudo] apt-get install libgeos++
```
2. Install proj
```
[sudo] apt-get install proj-bin
```
3. Install GDAL
```
[sudo] apt install gdal-bin
```
> If django has troubles with finding GDAL or geos, you can try 4 and 5 steps of installation process for macOS

# GeoDjango packages installation for macOS

1. Install Homebrew. If you already have it, you can skip this step
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
2. Install GDAL
```
brew install gdal
```
3. Install geos
```
brew install geos
```
> If django has troubles with finding GDAL or geos, you need to specify paths to them in .env file just as instructed above

4. Run below command to find GDAL path
```
find / -name "libgdal.dylib" -print 2>/dev/null
```
5. Run below command to find geos path
```
find / -name "libgeos.dylib" -print 2>/dev/null
```
