# Use an official Python runtime as a parent image, explicitly based on Debian 11 (Bullseye)
FROM python:3.10-slim-bullseye

# Set environment variables to prevent Python from writing .pyc files and to ensure output is sent straight to the terminal without buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for your application
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    unixodbc-dev \
    tesseract-ocr \
    poppler-utils \
    curl \
    gnupg \
    ca-certificates \
    libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

# Download and configure the Microsoft repository package
RUN curl -sSL https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -o packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb

# Update package lists and install the Microsoft ODBC Driver for SQL Server
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# (Optional) Remove `mssql-tools18` section

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application directories and main.py
COPY app/ /app/app/
COPY main.py /app/main.py

# Expose the Streamlit port
EXPOSE 8503

# Define the default command to run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8503", "--server.address=0.0.0.0"]
