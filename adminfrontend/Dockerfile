# Use a base Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy your static files
COPY . /app

# Expose the port the server will run on
EXPOSE 8009

# Start the server
CMD ["python", "-m", "http.server", "8009"]
