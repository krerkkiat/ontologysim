# pull official base image
FROM node:22.14.0-alpine3.20 AS builder

# set working directory
WORKDIR /app

# install app dependencies
COPY package.json ./
COPY package-lock.json ./

RUN npm install

# add app
COPY . ./

# Build the app
RUN npm run build

# The final image is just the built app with a static web server.
# In this case, static-web-server, you could use Nginx, Apache, etc.
FROM ghcr.io/static-web-server/static-web-server:2-alpine
COPY ./sws-config.toml ./
COPY --from=builder /app/build /public
CMD ["-w", "/sws-config.toml"]
