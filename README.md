# api_yamdb_

### Description:

The YaMDb project collects user reviews of various works.

### Tech:

Python, Django, DRF, JWT

### Installation instructions:

Clone the repository and go to the command line:

```git clone https://github.com/nasstiam/api_yamdb_```

```cd api_yamdb_```

Create and activate a virtual environment:

```python3 -m venv venv```

* If you have Linux/mac OS

    ```source venv/bin/activate```

* If you have windows

    ```source venv/scripts/activate```
    ```python -m pip install --upgrade pip```

Install the dependencies from the file requirements.txt:

```pip install -r requirements.txt```

Perform migrations:

```python manage.py migrate```

Launch the project:

```python manage.py runserver```
