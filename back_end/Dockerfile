FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

ENV VECTOR_STORE_DIR=/app/data/vector_store/faiss_index
ENV DOCS_PICKLE_PATH=/app/data/vector_store/all_docs.pkl

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
