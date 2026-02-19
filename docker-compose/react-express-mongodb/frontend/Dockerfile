#syntax=docker/dockerfile:1.4

# # Create image based on the official Node image from dockerhub
# FROM node:lts-buster AS development

# # Create app directory
# WORKDIR /usr/src/app

# # Copy dependency definitions
# COPY package.json /usr/src/app
# COPY package-lock.json /usr/src/app

# # Install dependecies
# #RUN npm set progress=false \
# #    && npm config set depth 0 \
# #    && npm i install
# RUN npm ci
# RUN rm -rf curl bash 

# # Get all the code needed to run the app
# COPY . /usr/src/app

# # Expose the port the app runs in
# EXPOSE 3000

# # Serve the app
# CMD ["npm", "start"]

# # Use nodemon for dev hot reload for the volumes you made
# #CMD ["npx", "nodemon", "server.js"]





















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
# CMD [ "npm", "start" ]

# this code for development and now i will write for production build 


FROM node:18-alpine AS builder
WORKDIR /app 
COPY ./package*.json .
RUN npm install 
COPY . .
RUN npm run build 
# cause this is vite create dist not build folder but it same 
FROM nginx:stable-alpine3.23-slim
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD [ "nginx", "-g", "daemon off;" ]
