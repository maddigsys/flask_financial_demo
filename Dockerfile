# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables for Python for better behavior in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define an argument for User ID, can be overridden at build time if needed
ARG UID=10001

# Create a non-root user and group for security
# This user will own and run the application
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY . .

# Change the ownership of the /app directory and its contents to the appuser
# This is important for security when running as a non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Make port 5000 available to the world outside this container
# This is the port your Flask app is configured to run on in app.py
EXPOSE 5000

# Define the command to run your application
# This will execute `python app.py`, which internally calls app.run(host='0.0.0.0', port=5000)
CMD [ "python", "app.py" ]
