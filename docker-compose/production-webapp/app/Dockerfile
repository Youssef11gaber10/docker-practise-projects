

FROM python:3.10 AS build

WORKDIR /app 

COPY requirements.txt .


RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt 
    
FROM python:3.10-slim

COPY --from=build /opt/venv /opt/venv 
# the venv must be align with /app
WORKDIR /app
COPY . .
ENV PATH="$PATH:/opt/venv/bin" 

EXPOSE 6000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000", "--loop", "asyncio"]
