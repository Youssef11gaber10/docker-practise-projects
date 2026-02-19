FROM python:3.9-slim AS deps

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir gunicorn 

FROM python:3.9-slim 
COPY --from=deps /opt/venv /opt/venv
WORKDIR /app
COPY . .
ENV PATH="$PATH:/opt/venv/bin"

EXPOSE 6000

CMD ["gunicorn", "app.app:app", "--bind", "0.0.0.0:6000", "--workers", "3"]