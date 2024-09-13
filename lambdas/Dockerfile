FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/lambdas

WORKDIR /lambdas
COPY requirements /lambdas/requirements

RUN pip install -r requirements/layers/requirements_core_lambda_layer.txt

COPY . /lambdas

ENTRYPOINT ["python", "scripts/batch_update_ods_code.py"]

# CMD ["python", "scripts/batch_update_ods_code.py"]

