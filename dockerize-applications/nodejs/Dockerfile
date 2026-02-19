FROM node:18-alpine AS deps

# like python install dependencies in one place and move it to smaller image
WORKDIR /app
COPY ./package*.json .
RUN npm install 
# the deps installed in node_modules and we will move it to smaller image

FROM node:18-slim

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD [ "node" , "server.js" ]