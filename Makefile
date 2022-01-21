SHELL := /bin/bash

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: ## Starts production containers
	find ./app -type d -name __pycache__ -exec rm -r {} \+

.PHONY: down
down: ## Stops all containers and removes volumes
	docker-compose -f docker-compose.devintegrated.yml down --volumes --remove-orphans
	
#######################
## BUILD IMAGES
#######################

.PHONY: devbuild
devbuild: ## Builds development containers
	docker-compose -f docker-compose.devsolo.yml --env-file=.env.solo build

.PHONY: prodbuild
prodbuild: ## Builds production containers
	docker-compose -f docker-compose.prod.yml build

#######################
## RUN CONTAINERS
#######################
.PHONY: solo
solo: down ## Starts solo development containers
	docker-compose -f docker-compose.devsolo.yml --env-file=.env.solo up -d

.PHONY: integrated
integrated: down ## Starts integrated development containers
	docker network create traefik-public || true
	docker-compose -f docker-compose.devintegrated.yml up -d

.PHONY: prod
prod: down ## Starts production containers
	docker-compose -f docker-compose.prod.yml up

#######################
## RUN TESTS
#######################

.PHONY: tests
tests: ## Starts test container
	#docker-compose exec googledrive pytest --cov=app --cov-report=term-missing app/tests
	docker-compose exec -T googledrive pytest app/tests

.PHONY: testing
testing: devbuild solo tests down ## Builds containers, runs them, runs test container and deletes all containers
