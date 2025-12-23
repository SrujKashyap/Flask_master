# 1️ Use the exact Python version your project uses
FROM python:3.9-slim

# Add environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 2️ Disable .pyc files (cleaner containers)
ENV PYTHONDONTWRITEBYTECODE=1

# 3️ Ensure logs appear instantly (important for Docker)
ENV PYTHONUNBUFFERED=1

# 4️ Set working directory inside container
WORKDIR /app

# 5️ Install OS-level dependencies (safe default)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 6️ Copy only requirements first (Docker caching optimization)
COPY requirements.txt .

# 7️ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 8️ Copy application code
COPY registration_module/ ./registration_module

# 9️ Ensure instance folder exists (SQLite DB lives here)
RUN mkdir -p registration_module/instance



# 11️ Expose the port Gunicorn listens on
EXPOSE 5000

# 12️ Start Flask app using Gunicorn
CMD sh -c "cd /app/registration_module && flask --app app:create_app db upgrade && gunicorn -w 2 -b 0.0.0.0:5000 registration_module.run:app"
