FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
RUN pip install --no-cache-dir imageio-ffmpeg
RUN python scripts/generate_camera_streams.py
RUN pip uninstall -y imageio-ffmpeg && rm -rf scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
