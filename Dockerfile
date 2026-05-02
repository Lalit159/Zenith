# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file into the container
COPY requirements.txt .

# 4. Install the dependencies
# --no-cache-dir is used to reduce the image size by not caching the installed packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your local code into the container
COPY . .

# 6. Expose the port FastAPI runs on
EXPOSE 8000

# 7. The command to run your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
