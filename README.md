# strong-mind-silverio
Fullstack engineer project for StrongMind Joshua Silverio

## Prerequisites
- Python 3.11.3
- pip 22.3.1
### Optional
- Docker 23.0.5
- Docker Compose v2.17.3

## Run Locally

```shell
  git clone 
  cd strong-mind-silverio/silverio_pizza
  pip install -r requirements.txt
```

### Create .env file 

```env
SECRET_KEY=<Secret-Key>
CHEF_USERNAME=chef
CHEF_PASSWORD=chef
OWNER_USERNAME=owner
OWNER_PASSWORD=owner
DEBUG=1
```

### Migrate, Create Users, and Start Server
```shell
  python manage.py makemigrations
  python manage.py migrate
  
  python manage.py makesuperuser
  # Username: admin
  # Email address: 
  # Password: admin
  python manage.py makesuperuser
  # Username: chef
  # Email address: 
  # Password: chef
  python manage.py makesuperuser
  # Username: owner
  # Email address: 
  # Password: owner
  
  python manage.py runserver 0.0.0.0:8000 --settings silverio_pizza.settings.local
```
- Navigate to localhost:8000/admin and login using admin. Add isChef and isOwner permissions to the respective user 
  in the Users database


## Run Locally with Docker-Compose

### Create .env file 

```env
SECRET_KEY=<Secret-Key>
CHEF_USERNAME=chef
CHEF_PASSWORD=chef
OWNER_USERNAME=owner
OWNER_PASSWORD=owner
DEBUG=1
```


## Start Stack

```shell
cd strong-mind-silverio/silverio_pizza
docker compose up -d --build 
```

### Migrate and Create Users
```shell
  #exec into web container
  
  python manage.py makemigrations
  python manage.py migrate
  
  python manage.py makesuperuser
  # Username: admin
  # Email address: 
  # Password: admin
  python manage.py makesuperuser
  # Username: chef
  # Email address: 
  # Password: chef
  python manage.py makesuperuser
  # Username: owner
  # Email address: 
  # Password: owner
```


## Tests
- To run tests locally use pytest
```shell
pytest --import-mode=importlib -sv
```

