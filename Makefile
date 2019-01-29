DOCKER_DIR := etc/docker
COMMON_COMPOSE_FILE := $(DOCKER_DIR)/docker-compose.common.yml
DEV_COMPOSE_FILE := $(DOCKER_DIR)/docker-compose.dev.yml
PROD_COMPOSE_FILE := $(DOCKER_DIR)/docker-compose.prod.yml

DEV_COMPOSE_ARGS := -f $(COMMON_COMPOSE_FILE) -f $(DEV_COMPOSE_FILE)
PROD_COMPOSE_ARGS := -f $(COMMON_COMPOSE_FILE) -f $(PROD_COMPOSE_FILE)

APP_NAME := graphql-geo
DB_NAME := postgis

ifeq ($(PROD_ENV),true)
	COMPOSE_ARGS := $(PROD_COMPOSE_ARGS)
else
    COMPOSE_ARGS := $(DEV_COMPOSE_ARGS)
endif

COMPOSE_CMD := docker-compose $(COMPOSE_ARGS)

build:
	$(COMPOSE_CMD) build

start:
	$(COMPOSE_CMD) start

stop:
	$(COMPOSE_CMD) stop

restart:
	$(COMPOSE_CMD) restart

restart-app:
	$(COMPOSE_CMD) restart $(APP_NAME)

restart-db:
	$(COMPOSE_CMD) restart $(APP_NAME)

up:
	$(COMPOSE_CMD) up --build -d

down:
	$(COMPOSE_CMD) down

down-volumes:
	$(COMPOSE_CMD) down -v

logs:
	$(COMPOSE_CMD) logs

shell:
	$(COMPOSE_CMD) run graphql-geo /bin/sh

test:
	$(COMPOSE_CMD) run graphql-geo /bin/sh -c "python geo/test/integration.py"

alembic-upgrade:
	$(COMPOSE_CMD) run graphql-geo /bin/sh -c "alembic upgrade head"

status:
	$(COMPOSE_CMD) status

black:
	black --exclude venv/ .

.PHONY:
	build
	start
	stop
	restart
	restart-app
	restart-db
	up
	down
	down-volumes
	logs
	shell
	test
	alembic-upgrade
	status
	black