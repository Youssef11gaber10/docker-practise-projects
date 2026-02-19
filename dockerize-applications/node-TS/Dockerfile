FROM node:18-alpine AS builder

# this not like normal nodejs app its with typescript so build the app and move the dist to smaller image
WORKDIR /app
COPY ./package*.json .
RUN npm install 
COPY . . 
#build the app and move the dist to smaller image
RUN npm run lint 
RUN npm run build 
# under dist you will find tsc compiled code and we will move it to smaller image

FROM node:18-slim

WORKDIR /app
COPY ./package*.json . 
# here install only production dependencies  not all 
RUN npm install --only=production 
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD [ "node" , "dist/index.js" ]