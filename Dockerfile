FROM python:3.12-slim AS base

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the source code
COPY . .

RUN chmod +x entrypoint.sh

# Run the application
CMD ["/app/entrypoint.sh"]