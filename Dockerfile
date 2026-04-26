FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mc_pricer/ ./mc_pricer/
COPY backend/ ./backend/
COPY setup.cfg ./
COPY pyproject.toml ./

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]