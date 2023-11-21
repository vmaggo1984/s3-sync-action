FROM python:3.10
ARG POETRY_VERSION="1.3.1"

# Ensure that the python output is sent straight to terminal
# Ensure that poetry creates virtualenvs in the cache directory
# Set cache directory for poetry to the directory we created
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_IN_PROJECT false
ENV POETRY_CACHE_DIR /cache/poetry

# /cache for Poetry Cache
RUN mkdir /cache
RUN python3 -m pip install poetry=="${POETRY_VERSION}"
