FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy server + knowledge base
COPY . .

# Cloud Run convention
ENV PORT=8080
EXPOSE 8080

CMD ["python", "server.py"]

