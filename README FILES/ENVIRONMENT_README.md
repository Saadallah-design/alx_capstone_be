# Django Environment Variable Management: python-dotenv vs django-environ

## Overview
Django projects often use environment variables to manage secrets and configuration. Two popular libraries for this are:
- **python-dotenv**: Loads variables from a `.env` file into the environment.
- **django-environ**: A Django-specific library that loads and parses environment variables, supporting type conversion and `.env` files.

---

## 1. Using `python-dotenv`

### Installation
```
pip install python-dotenv
```

### Usage in `settings.py`
```python
from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB_NAME'),
        'USER': os.getenv('POSTGRES_DB_USER'),
        'PASSWORD': os.getenv('POSTGRES_DB_PASSWORD'),
        'HOST': os.getenv('POSTGRES_DB_HOST'),
        'PORT': os.getenv('POSTGRES_DB_PORT'),
    }
}
```

---

## 2. Using `django-environ`

### Installation
```
pip install django-environ
```

### Usage in `settings.py`
```python
import environ
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, 'carRentalConfig/.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB_NAME'),
        'USER': env('POSTGRES_DB_USER'),
        'PASSWORD': env('POSTGRES_DB_PASSWORD'),
        'HOST': env('POSTGRES_DB_HOST'),
        'PORT': env('POSTGRES_DB_PORT'),
    }
}
```

---

## 3. Should You Use Both?
**No.** Use only one method in your project to avoid confusion and bugs. 
- If you want simple variable loading, use `python-dotenv`.
- If you want type conversion and more Django-specific features, use `django-environ`.

---

## 4. Best Practices
- Always add `.env` to your `.gitignore`.
- Never commit secrets to version control.
- Use quotes in `.env` if your value contains special characters (like `#`).
- For production, set `DEBUG=False` and configure `ALLOWED_HOSTS`.

---

## 5. Example `.env` File
```
SECRET_KEY='your-secret-key-with-#-inside'
DEBUG=True
POSTGRES_DB_NAME=car_rental_db
POSTGRES_DB_USER=your_db_user
POSTGRES_DB_PASSWORD=your_db_password
POSTGRES_DB_HOST=localhost
POSTGRES_DB_PORT=5432
```

---

## 6. References
- [python-dotenv documentation](https://pypi.org/project/python-dotenv/)
- [django-environ documentation](https://django-environ.readthedocs.io/en/latest/)
