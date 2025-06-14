FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Configure DNS. Some build environments have a read-only resolv.conf, so
# ignore any failure when writing the file.
RUN echo 'nameserver 1.1.1.1\nnameserver 8.8.8.8' | tee /etc/resolv.conf >/dev/null || true
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
