# 1. Use Python slim base image
FROM python:3.12.0-slim-bookworm

# 2. Ensure output is logged immediately
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 3. Set application directory
ENV APP=/app
WORKDIR $APP

# 4. Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install Python packages
COPY requirements.txt $APP/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 6. Copy application code
COPY . $APP

# 7. Expose port
EXPOSE 8000

# 8. Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# 9. Define entrypoint
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]

# 10. Default command to start the application
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]
