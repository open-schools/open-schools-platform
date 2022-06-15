# Deploy

---

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