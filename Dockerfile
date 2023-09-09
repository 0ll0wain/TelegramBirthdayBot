# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY BirthdayBot.py /app
COPY credentials.py /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define a volume where your persistent data will be stored
VOLUME /data

# Run script.py when the container launches
CMD ["python", "BirthdayBot.py"]

