FROM python:3.12-slim

# Update package lists and install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Ensure entrypoint.sh is executable

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
