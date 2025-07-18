# Usar Python 3.12 slim como base para menor tamanho de imagem
FROM python:3.12-slim AS base

# Metadados da imagem
LABEL maintainer="acompanhamento-team"
LABEL description="Microservice de Acompanhamento de Pedidos"
LABEL version="1.0.0"

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1

# Instalar dependências do sistema, Poetry e criar usuário
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry="$POETRY_VERSION" \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock ./

# Instalar dependências Python
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-root --no-ansi \
    && rm -rf "$POETRY_CACHE_DIR"

# Copiar código da aplicação
COPY app/ ./app/
COPY pytest.ini ./

# Criar diretórios necessários e alterar propriedade
RUN mkdir -p /app/logs /app/temp \
    && chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta padrão para aplicações FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão para executar a aplicação
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
