

FROM python:3.10 AS build

WORKDIR /app 

COPY requirements.txt .

# i want make venv to collect all dependencies in one place and move it to smaller image

# now we have all dependencies in /opt/venv and we can move it to smaller image
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt 
FROM python:3.10-slim

COPY --from=build /opt/venv /opt/venv 
# the venv must be align with /app
WORKDIR /app
COPY . .
ENV PATH="$PATH:/opt/venv/bin" 
# ENV PATH="/opt/venv/bin:$PATH" # best practice 


EXPOSE 6000


CMD ["uvicorn", "asgi_app:ASGIApplication", "--host", "0.0.0.0", "--port", "6000", "--loop", "asyncio"]
