# All the configurable parameters are in the file '.config'
include .config
export

# Build proxy server and redis instance
build:
	@echo Building proxy server docker
	docker-compose build

# Run all tests
run:
	@echo Running the proxy server only
	docker-compose up proxy

# Build proxy server then run all tests
test: build
	docker-compose up
	# TODO: call integration tests here

logs:
	docker-compose logs
# Closes app
exit:
	@echo Shutting down proxy server
	docker-compose stop