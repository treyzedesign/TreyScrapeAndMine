# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /

# Copy the application code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]