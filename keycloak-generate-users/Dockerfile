# Use the Python UBI base image
FROM registry.access.redhat.com/ubi8/python-39

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install additional system dependencies if needed (e.g., GCC for compiling some Python libraries)
USER root
RUN yum -y update && yum -y install gcc && yum clean all

# Switch to non-root user provided by the UBI image
USER 1001

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Default command to run the script
CMD ["python", "generate-users-and-group.py"]
