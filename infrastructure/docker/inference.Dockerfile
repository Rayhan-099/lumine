FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for OpenCV and other ML tools
RUN apt-get update \
  && apt-get -y install libgl1-mesa-glx libglib2.0-0 \
  && apt-get clean

# Install Python dependencies
COPY inference/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY inference/ .

# Command to run Celery worker
CMD ["celery", "-A", "worker.main", "worker", "--loglevel=info"]
