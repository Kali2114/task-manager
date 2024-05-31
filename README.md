# Task Manager Application

## Setup and Installation

### Requirements
- Python 3.x
- pip
- virtualenv (optional but recommended)
- Docker (for PostgreSQL database setup)
- Docker Compose

### Installation Steps

1. **Clone the repository**:
    ```sh
    git clone https://github.com/your-repo/task-manager.git
    cd task-manager
    ```

2. **Create a virtual environment** (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the project root directory with the following content:
      ```
      DJANGO_SETTINGS_MODULE=config.settings
      DEBUG=True
      SECRET_KEY=your_secret_key
      DB_HOST=db
      DB_NAME=taskmanager
      DB_USER=postgres
      DB_PASS=your_password
      ```

5. **Start the PostgreSQL database using Docker Compose**:
    ```sh
    docker-compose up -d
    ```

6. **Run database migrations**:
    ```sh
    python manage.py makemigrations
    ```

7. **Create a superuser** (optional but recommended for admin access):
    ```sh
    python manage.py createsuperuser
    ```

8. **Run the development server**:
    ```sh
    python manage.py runserver
    ```

## Running Tests

### Using pytest

To run tests using `pytest`, ensure you have `pytest` and `pytest-django` installed and simply run:

```sh
pytest
```

### Using Django's test framework within Docker
To run tests using Django's built-in test framework, use the following command:
```
docker-compose run --rm app sh -c "python manage.py test"
```

## Code Formatting and Linting

### Using flake 8
flake8 is used for linting the code. To run flake8, use:
```
flake8 .
```

### Using black
black is used for code formatting. To format your code using black, use:
```
black .
```

## API Documentation

### Authentication

- Login and obtain token:
```
curl -X POST -d "email=user@example.com&password=password" http://localhost:8000/api/user/token/
```

### Task Endpoints

- Create a new task:
```
curl -X POST -H "Authorization: Token your_token" -d "name=New Task&description=Task description&status=new" http://localhost:8000/api/task/tasks/
```

- List all tasks:
```
curl -H "Authorization: Token your_token" http://localhost:8000/api/task/tasks/
```

- Retrieve a specific task:
```
curl -H "Authorization: Token your_token" http://localhost:8000/api/task/tasks/1/
```

- Update a task:
```
curl -X PUT -H "Authorization: Token your_token" -d "name=Updated Task&description=Updated description&status=done" http://localhost:8000/api/task/tasks/1/
```

- Delete a task:
```
curl -X DELETE -H "Authorization: Token your_token" http://localhost:8000/api/task/tasks/1/
```

## Notes

* Docker Compose: Use Docker Compose to build and start the PostgreSQL database. 
* Starting the server: Ensure the Django application is running with Gunicorn (docker-compose up) before executing curl commands.
* Testing: Configure pytest as instructed and ensure all tests pass successfully. Alternatively, you can run tests using Django's test framework within Docker.
* Gunicorn: The application uses Gunicorn as the WSGI server for better performance and reliability in production environments.

## License
This project is licensed under the GNU General Public License v3.0. For more details, see the LICENSE file.

```
This `README.md` file provides comprehensive instructions for setting up, running, and testing your Django application using Docker, Docker Compose, and Gunicorn. It also includes examples of how to interact with the API using `curl` commands.
```