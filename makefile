default: help

.PHONY: Install
install:
	cd ./app && npm install

.PHONY: Clean install
clean-install:
	cd ./app && npm ci

.PHONY: Start
start:
	cd ./app && npm start

.PHONY: Test
test:
	cd ./app && npm run test-all

.PHONY: Build
build:
	cd ./app && npm run build

.PHONY: Docker Up
docker-up:
	cd ./app && docker-compose up -d

.PHONY: Docker Down
docker-down:
	cd ./app && docker-compose down -d