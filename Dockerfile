# Use a different image for building because we need git to install whisper
FROM python:3.10 AS build

# Create virtual environment
RUN python3 -m venv /venv

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy requirements.txt
ADD ./core_requirements.txt ./requirements.txt

# Install whisper before other dependencies to satisfy stable-ts
RUN /venv/bin/pip install --no-cache-dir git+https://github.com/openai/whisper.git
# Install remaining dependencies
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt
# Install gunicorn for production server
RUN /venv/bin/pip install --no-cache-dir gunicorn==20.1.0

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim as production

# Copy installed dependencies from build
COPY --from=build /venv /venv

# Install ffmpeg runtime library
RUN apt-get -qy update && apt-get -qy install ffmpeg && \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Specify environment variables MUST BE SET
ENV OPENAI_API_KEY ""
ENV YOUTUBE_API_KEY ""

# TODO: Convert to use gunicorn
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
ENV HOST "0.0.0.0"
ENV PORT "8080"
CMD exec /venv/bin/gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.server.index:app
