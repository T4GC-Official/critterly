# Use a Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and the script into the container
COPY excel_to_json.py /app/excel_to_json.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Set the entry point to run the script
ENTRYPOINT ["python", "/app/excel_to_json.py"]
