clean: clean-build clean-py clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-py:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +	

clean-test:
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.coverage' -exec rm -fr {} +
	find . -name 'htmlcov' -exec rm -fr {} +
	find . -name '.cache' -exec rm -fr {} +

format:
	./lambdas/venv/bin/python3 -m black . &&\
	ruff check . --fix
	./lambdas/venv/bin/python3 -m isort lambdas/handlers/. 
	./lambdas/venv/bin/python3 -m isort lambdas/models/. 
	./lambdas/venv/bin/python3 -m isort lambdas/utils/. 
	./lambdas/venv/bin/python3 -m isort lambdas/services/.
	./lambdas/venv/bin/python3 -m isort lambdas/enums/.
	./lambdas/venv/bin/python3 -m isort lambdas/tests/. 

test-unit:
	cd ./lambdas && ./venv/bin/python3 -m pytest tests/

test-unit-collect:
	cd ./lambdas && ./venv/bin/python3 -m pytest tests/ --collect-only

env:
	rm -rf lambdas/venv || true
	python3 -m venv ./lambdas/venv
	./lambdas/venv/bin/pip3 install --upgrade pip
	./lambdas/venv/bin/pip3 install -r lambdas/requirements.txt
	./lambdas/venv/bin/pip3 install -r lambdas/requirements-test.txt

zip:
	rm -rf ./lambdas/package_$(lambda_name) || true 
	mkdir ./lambdas/package_$(lambda_name)
	./lambdas/venv/bin/pip3 install --cache-dir .pip_cache -r lambdas/requirements.txt -t ./lambdas/package_$(lambda_name)
	mkdir ./lambdas/package_$(lambda_name)/handlers
	cp -r lambdas/handlers/$(lambda_name).py lambdas/package_$(lambda_name)/handlers
	cp -r lambdas/utils lambdas/package_$(lambda_name)
	cp -r lambdas/models lambdas/package_$(lambda_name)
	cp -r lambdas/services lambdas/package_$(lambda_name)
	cp -r lambdas/enums lambdas/package_$(lambda_name)
	cd ./lambdas/package_$(lambda_name); zip -r ../../package_lambdas_$(lambda_name).zip .
	rm -rf ./lambdas/package_$(lambda_name)
	cd ../..

package: format zip

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
	cd ./app && docker-compose down

.PHONY: Cypress Run
cypress-open:
	cd ./app && npx cypress open