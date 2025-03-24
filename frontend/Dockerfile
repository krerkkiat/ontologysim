# pull official base image
FROM node:16.13.2-alpine3.14 AS builder

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH


# install app dependencies
COPY package.json ./
COPY package-lock.json ./

RUN npm cache clean --force
RUN npm install --save-dev  --unsafe-perm node-sass -g
RUN npm rebuild node-sass
RUN npm install react-scripts@4.0.3 -g --silent
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
