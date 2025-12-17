# 1️⃣ Use the exact Python version your project uses
FROM python:3.9-slim

# Add environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 2️⃣ Disable .pyc files (cleaner containers)
ENV PYTHONDONTWRITEBYTECODE=1

# 3️⃣ Ensure logs appear instantly (important for Docker)
ENV PYTHONUNBUFFERED=1

# 4️⃣ Set working directory inside container
WORKDIR /app

# 5️⃣ Install OS-level dependencies (safe default)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 6️⃣ Copy only requirements first (Docker caching optimization)
COPY requirements.txt .

# 7️⃣ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 8️⃣ Copy application code
COPY registration_module ./registration_module

# 9️⃣ Ensure instance folder exists (SQLite DB lives here)
RUN mkdir -p instance

# 🔟 Expose the port Gunicorn listens on
EXPOSE 5000

# 1️⃣1️⃣ Start Flask app using Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "registration_module.run:app"]
