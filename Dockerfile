FROM python:3.11-slim as builder

WORKDIR /backend
COPY pyproject.toml .

RUN pip install --no-cache-dir pip-tools && \
    pip-compile pyproject.toml --output-file requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

COPY src src/

FROM python:3.11-slim

WORKDIR /backend

COPY --from=builder /backend/src src/
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

ENV PYTHONPATH="/backend/src:$PYTHONPATH"

EXPOSE 8000

CMD ["python", "src/backend/run.py"]
