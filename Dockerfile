FROM python:3.12.8-slim

WORKDIR /app

COPY .venv/lib/python3.12/site-packages/langchain_google_community /tmp/langchain_google_community

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN rm -rf /usr/local/lib/python3.12/langchain-google-community && \
    cp -r /tmp/langchain_google_community /usr/local/lib/python3.12/site-packages/

COPY . .

CMD ["python3", "main.py"]
