FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/lambdas

WORKDIR /lambdas

COPY . /lambdas

RUN pip install -r requirements/layers/requirements_core_lambda_layer.txt

ENTRYPOINT ["python", "scripts/batch_update_ods_code.py"]

# CMD ["python", "scripts/batch_update_ods_code.py"]

