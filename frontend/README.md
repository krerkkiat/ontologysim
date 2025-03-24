Ontologysim React: a Front end Development for ontologysim
===========================================================================

Ontologysim React is used to visualize the simulation runs created with ontologysim. Ontologysim react is only used as frontend, all calculations are done in the library ontologysim.

Ontologysim React main features are:

* visualisation of production simulation
* kpi analyse
* providing event overview

## Local Development Setup

Install the following software pacakges

- [Node.js 22.14.0](https://nodejs.org/en/)
- [Docker and docker-compose](https://www.docker.com/products/docker-desktop)

Install the nodejs dependencies with

```console
npm install
```

Create a `.env.local` file (it will not be tracked by Git and that is intentional)
with the content from `.env.sample`. If you are deploying to a production environment,
you can change where the API server is located using this variable.

### Useful Commands

Run the development server with

```console
npm run serve
```

Build the application with

```console
npm run build
```

Build a container image (separately from the backend and without docker compose) with

```console
docker build -t ontologysim_frontend .
```

Run the container (separately from the backend and without docker compose) with

```console
docker run --rm -it ontologysim_frontend:latest
```

This will serve the built application with [static-web-server](https://static-web-server.net/).
