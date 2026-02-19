# # syntax=docker/dockerfile:1.4

# FROM node:lts-buster-slim AS development

# # Create app directory
# WORKDIR /usr/src/app

# COPY package.json /usr/src/app/package.json
# COPY package-lock.json /usr/src/app/package-lock.json
# RUN npm ci

# COPY . /usr/src/app

# #this is repeating cause he also write -expose :3000 in docker compose 
# EXPOSE 3000 

# CMD [ "npm", "run", "dev" ]

# FROM development as dev-envs
# RUN <<EOF
# apt-get update
# apt-get install -y --no-install-recommends git
# EOF

# RUN <<EOF
# useradd -s /bin/bash -m vscode
# groupadd docker
# usermod -aG docker vscode
# EOF
# # install Docker tools (cli, buildx, compose)
# COPY --from=gloursdocker/docker / /
# CMD [ "npm", "run", "dev" ]

# # Use nodemon for dev hot reload for the volumes you made to live development
# # CMD ["npx", "nodemon", "server.js"]


FROM node:18-alpine AS deps

# like python install dependencies in one place and move it to smaller image
WORKDIR /app
COPY ./package*.json .
# RUN npm install 
RUN npm ci --only=production 
# here it was develpment so install only the production package
# the deps installed in node_modules and we will move it to smaller image

FROM node:18-slim

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD [ "node" , "server.js" ]