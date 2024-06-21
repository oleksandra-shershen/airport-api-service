# Airport API Service
## Introduction
The Airport API Service is designed to track flights from airports across the globe. The system includes features for managing airports, routes, airplanes, flights, crews, tickets, and orders. The provided database structure allows for efficient tracking and management of these entities.

## Installation & Run

### Prerequisites:
* Python 3.8+
* Docker Desktop

### Set enviroment variable:
- Copy and rename the **.env.sample** file to **.env** 
- Open the .env file and edit the environment variables 
- Save the .env file securely 
- Make sure the .env file is in .gitignore

On Windows:
```python
python -m venv venv 
venv\Scripts\activate
 ```

 On UNIX or macOS:
```python
python3 -m venv venv 
source venv/bin/activate
 ```

### Install requirements 
```python
docker-compose up --build
```

### (Optional) Create a superuser
If you want to perform all available features, create a superuser account in a new terminal:
```python
docker-compose exec -it airport /bin/sh
python manage.py createsuperuser
```

### Go to site [http://localhost:8001/](http://localhost:8001/)

### Features:
* JWT Authenticated
* Admin panel /admin/
* Documentation located in api/doc/swagger/
* Managing orders and tickets
* 
