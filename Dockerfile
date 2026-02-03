FROM python:3.12.4-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .
RUN uv pip install --system .

COPY . .

ENV PYTHONPATH=/app/src

COPY entrypoint.sh /entrypoint.sh
RUN sed -i '1s/^\xEF\xBB\xBF//' /entrypoint.sh \
 && sed -i 's/\r$//' /entrypoint.sh \
 && chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]
