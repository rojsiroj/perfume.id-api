# perfume.id API

How to test this?

1. [Install Docker Compose](https://docs.docker.com/compose/install/)
1. Clone this repository
1. Run all containers with `docker compose up`
1. Run all containers with `docker compose run --rm app sh -c "python manage.py test && flake8"` to run unit test and linter
