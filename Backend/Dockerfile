# Use an official Python runtime as the parent image
FROM python:3.8

# Set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \ 
  && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
COPY /screenshots /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps
# Copy the current directory contents into the container at /app
COPY . /app/

# Run the web server using uvicorn
# Note: adjust the host and port as necessary
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
