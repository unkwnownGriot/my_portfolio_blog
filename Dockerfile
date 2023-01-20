# Get Base OS
FROM alpine:latest

# Install python3 and pip
RUN apk add --no-cache python3-dev && Install --upgrade pip

# Set Working Directory
WORKDIR /app

# Copy Files Into Working Directory
COPY . /app

# Expose Flask Port
EXPOSE 5000

# Run With Development Server
ENTRYPOINT ["python3"]
CMD ["run_app.py"]

