# Deploy

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
6. Migrate
```
python manage.py migrate
```
7. Run django server
```
python manage.py runserver [port]
```
8. Install pre-commit hooks
```
pre-commit install
```
9. Install pre-push hooks
```
pre-commit install --hook-type pre-push
```
10. Install GeoDjango packages

> GeoDjango packages installation for windows

1. Download GDAL‑3.2.3‑cp39‑cp39‑win_amd64.whl from https://www.lfd.uci.edu/~gohlke/pythonlibs/
2. Install GDAL
```
pip install <path-to-GDAL‑3.2.3‑cp39‑cp39‑win_amd64.whl>
```

3. Open CLI for open-schools-platform docker container. You can do it from docker desktop

4. Connect to DB via psql
```
psql postgres://postgres:postgres@localhost:5432/local_db
```
5. Create postgis extension
```
CREATE EXTENSION postgis;
```
> If creating extension results in some kind of error, you can do 6 and 7 steps and retry creating extension

6. In CLI run
```
apt-get update
```
7. Install postgis
```
apt install postgis postgresql-14-postgis-scripts
```

> GeoDjango packages installation for linux

1. Install geos
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
4. Do steps 3-7 from GeoDjango windows installation 

> GeoDjango packages installation for macOS

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
4. Do steps 3-7 from GeoDjango windows installation

> If django has troubles with finding GDAL or geos, you can specify path to them in .env file (works for macOS)

1. Run below command to find GDAL path
```
find / -name "libgdal.dylib" -print 2>/dev/null
```
2. Run below command to find geos path
```
find / -name "libgeos.dylib" -print 2>/dev/null
```
3. In .env file write
```
GDAL_LIBRARY_PATH=<path-to-file>
GEOS_LIBRARY_PATH=<path-to-file>
GEO_DJANGO_CUSTOM_PATHS=True
```
> You can also specify OSGEO4W_ROOT, GDAL_DATA and PROJ_LIB paths in .env file