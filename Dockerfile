# Use Python 3.8 as the base image, slim version for a smaller footprint
FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache during builds
COPY requirements.txt /app/

# Upgrade pip to the latest version to ensure smooth installation of packages
RUN pip install --upgrade pip

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port that the app will run on (e.g., 8000 for Django)
EXPOSE 8000

# Set the default command to run the application (Django development server in this case)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
