FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/lambdas

WORKDIR /lambdas
COPY ../../requirements /lambdas/requirements

RUN pip install -r requirements/layers/requirements_core_lambda_layer.txt
RUN pip install -r requirements/layers/requirements_data_lambda_layer.txt

COPY ../../ /lambdas

ENTRYPOINT ["python", "ecs/data_collection/main.py"]
