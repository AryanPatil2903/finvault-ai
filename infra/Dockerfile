# ── Stage 1: Python backend builder ──────────────────────────────────────────
FROM python:3.11-slim AS backend-builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2: Node.js frontend builder ────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /ui
COPY ui/package*.json ./
RUN npm ci
COPY ui/ .
RUN npm run build

# ── Stage 3: Production runtime ───────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN addgroup --gid 1001 finvault && adduser --uid 1001 --gid 1001 --no-create-home finvault

WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=backend-builder /root/.local /home/finvault/.local

# Copy application source
COPY --chown=finvault:finvault . .

# Copy built frontend into static serving directory
COPY --from=frontend-builder --chown=finvault:finvault /ui/dist /app/ui/dist

# Create required directories
RUN mkdir -p logs models data/raw data/processed data/outputs && \
    chown -R finvault:finvault /app

USER finvault

# Ensure local Python packages are on PATH
ENV PATH=/home/finvault/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]