# To run this setup manually with docker commands (without docker-compose), use the following steps:

# 1. Create Docker volumes for data persistence
docker volume create redis_data
docker volume create mysql_data

# 2. Start the MySQL container
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=mydb \
  -p 3306:3306 \
  -v mysql_data:/var/lib/mysql \
  mysql:8.0 \
  --default-authentication-plugin=mysql_native_password

# 3. Start the Redis container
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:6.2-alpine

# 4. Build and run the web application container
# (Assuming your Dockerfile is in the current directory)
docker build -t my-web-app .

docker run -d \
  --name web \
  -p 6000:6000 \
  --env REDIS_HOST=redis \
  --env REDIS_PORT=6379 \
  --env MYSQL_HOST=mysql \
  --env MYSQL_USER=root \
  --env MYSQL_PASSWORD=password \
  --env MYSQL_DATABASE=mydb \
  --link redis \
  --link mysql \
  my-web-app

# Note:
# --link is deprecated but works for simple local development. For production, use user-defined networks.
# For a more robust setup, create a custom network and attach all containers to it:
# docker network create myapp-net
# Then add: --network myapp-net to each docker run command above.

# End of docker-compose.yml (no changes to the YAML itself)
