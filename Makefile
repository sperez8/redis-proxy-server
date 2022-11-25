# All configurable parameters are in the file '.config'
include .config
export

build:
	@echo Building proxy server and test containers
	docker-compose build

run_proxy:
	@echo Builing and running the proxy server only
	docker-compose build proxy
	docker-compose up proxy

test: build
	@echo Running proxy server and integration tests
	docker-compose up

logs:
	docker-compose logs

ps:
	docker-compose ps

exit:
	@echo Shutting down containers
	docker-compose stop