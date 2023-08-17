# Use an official Python runtime as the base image
FROM python:3.11.4

# Set environment variables for djangostock
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE djangostock.settings.local

# Set the working directory in the container
WORKDIR /djangostock

# Copy the requirements file into the container at /djangostock/requirements
COPY requirements requirements

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements/local.txt

# Copy the current directory contents into the container at /djangostock
COPY . /djangostock/

# Expose port 8000 (Daphne)
EXPOSE 8000

# Run Daphne ASGI server
CMD ["daphne", "djangostock.asgi:application", "-b", "0.0.0.0", "-p", "8000"]
