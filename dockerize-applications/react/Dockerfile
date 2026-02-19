FROM node:18-alpine AS builder
WORKDIR /app 
COPY ./package*.json .
RUN npm install 
COPY . .
RUN npm run build 
# cause this is vite create dist not build folder but it same 
FROM nginx:stable-alpine3.23-slim
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD [ "nginx", "-g", "daemon off;" ]
