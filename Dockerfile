# Inherit from python official Image
FROM python:3.8-slim-buster

# Copy project to app folder
COPY . /app

# Create Working Directory
WORKDIR /app

# Install requirements file
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

# Expose Flask Port
EXPOSE 5000

# Run With Development Server
ENTRYPOINT ["python3"]
CMD ["run_app.py"]

