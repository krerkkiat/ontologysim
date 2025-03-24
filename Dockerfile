FROM debian:12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y python3 python3-dev python3-pip unixodbc-dev python3-cffi;
# Install OpenJDK-8
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

RUN apt-get update && \
    apt-get install -y libffi-dev && \
    apt-get clean;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
RUN export JAVA_HOME

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"
RUN uv venv --python 3.11

COPY requirements.txt requirements.txt
RUN uv pip install -r requirements.txt

# NOTE(KC): This will copy the frontend as well.
COPY --exclude=frontend/* . .

CMD ["uv", "run", "ontologysim/Flask/FlaskMain.py"]
