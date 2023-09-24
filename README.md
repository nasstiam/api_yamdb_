# api_yamdb_

### Description:

The YaMDb project collects user reviews of various works. Titles have different Genres and Categories. 
Only Administrator can add Titles, Categories adn Genres. Users can leave only one text Review on a Title 
and give a score to Title. Users can comment Reviews. Only Authenticated users can leave reviews, comments 
and give ratings. 
User can register by himself or Admin can register User. User gets confirmation code on email, which allows
to get JWT-Token. 

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
