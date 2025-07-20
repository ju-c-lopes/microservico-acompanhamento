"""
Configurações centralizadas da aplicação.
Este módulo centraliza todas as configurações necessárias para o funcionamento
da API de acompanhamento, incluindo configurações de ambiente, logging e integração.
"""

import os
from functools import lru_cache
from typing import List, Optional


class Settings:
    """Configurações da aplicação carregadas do ambiente."""

    def __init__(self):
        """Inicializa e valida as configurações."""
        # === Configurações da API ===
        self.app_name = os.getenv("APP_NAME", "Microserviço Acompanhamento")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.app_description = os.getenv(
            "APP_DESCRIPTION",
            "API para acompanhamento de pedidos e status de pagamento",
        )
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # === Configurações do Servidor ===
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.reload = os.getenv("RELOAD", "false").lower() == "true"

        # === Configurações de CORS ===
        cors_origins_str = os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
        )
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        self.cors_allow_credentials = (
            os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        )
        cors_methods_str = os.getenv(
            "CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS"
        )
        self.cors_allow_methods = [
            method.strip() for method in cors_methods_str.split(",")
        ]
        cors_headers_str = os.getenv("CORS_ALLOW_HEADERS", "*")
        self.cors_allow_headers = [
            header.strip() for header in cors_headers_str.split(",")
        ]

        # === Configurações do Banco de Dados ===
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost/acompanhamento",
        )
        self.database_echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.database_pool_size = int(os.getenv("DATABASE_POOL_SIZE", "5"))
        self.database_max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

        # === Configurações do Kafka ===
        self.kafka_bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self.kafka_group_id = os.getenv("KAFKA_GROUP_ID", "acompanhamento-service")
        self.kafka_auto_offset_reset = os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest")

        # Tópicos Kafka
        self.kafka_topic_pedido_criado = os.getenv(
            "KAFKA_TOPIC_PEDIDO_CRIADO", "pedido.criado"
        )
        self.kafka_topic_pagamento_processado = os.getenv(
            "KAFKA_TOPIC_PAGAMENTO_PROCESSADO", "pagamento.processado"
        )
        self.kafka_topic_pedido_atualizado = os.getenv(
            "KAFKA_TOPIC_PEDIDO_ATUALIZADO", "pedido.atualizado"
        )

        # === Configurações de Logging ===
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = os.getenv(
            "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.log_file = os.getenv("LOG_FILE")

        # === Configurações de Segurança ===
        self.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # === Configurações de Performance ===
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_request_size = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB

        # === Configurações de Monitoramento ===
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.metrics_path = os.getenv("METRICS_PATH", "/metrics")
        self.health_check_path = os.getenv("HEALTH_CHECK_PATH", "/health")

        # === Configurações de Integração Externa ===
        self.external_api_timeout = int(os.getenv("EXTERNAL_API_TIMEOUT", "10"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "1"))

        # Validações
        self._validate_log_level()
        self._validate_kafka_offset_reset()

    def _validate_log_level(self):
        """Valida o nível de log."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"Log level deve ser um de: {valid_levels}")

    def _validate_kafka_offset_reset(self):
        """Valida a configuração de offset reset do Kafka."""
        valid_values = ["latest", "earliest", "none"]
        if self.kafka_auto_offset_reset not in valid_values:
            raise ValueError(f"kafka_auto_offset_reset deve ser um de: {valid_values}")


class DevelopmentSettings(Settings):
    """Configurações específicas para desenvolvimento."""

    def __init__(self):
        super().__init__()
        self.debug = True
        self.reload = True
        self.database_echo = True
        self.log_level = "DEBUG"
        self.cors_origins = ["*"]  # Mais permissivo em desenvolvimento


class ProductionSettings(Settings):
    """Configurações específicas para produção."""

    def __init__(self):
        super().__init__()
        self.debug = False
        self.reload = False
        self.database_echo = False
        self.log_level = "INFO"
        # CORS origins devem ser configurados explicitamente em produção


class TestSettings(Settings):
    """Configurações específicas para testes."""

    def __init__(self):
        super().__init__()
        self.debug = True
        self.database_url = "sqlite+aiosqlite:///./test.db"
        self.kafka_bootstrap_servers = "localhost:9092"  # Mock em testes
        self.log_level = "WARNING"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações baseadas no ambiente.
    Usa cache para evitar reprocessamento das configurações.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()


# Configurações globais
settings = get_settings()


def configure_logging():
    """Configura o sistema de logging da aplicação."""
    import logging.config

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING",  # Reduz logs de acesso em produção
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if not settings.database_echo else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # Adiciona handler de arquivo se configurado
    if settings.log_file:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.log_level,
            "formatter": "detailed",
            "filename": settings.log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        # Adiciona o handler de arquivo a todos os loggers
        for logger in logging_config["loggers"].values():
            logger["handlers"].append("file")

    logging.config.dictConfig(logging_config)


def get_cors_config() -> dict:
    """Retorna a configuração de CORS para o FastAPI."""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": settings.cors_allow_credentials,
        "allow_methods": settings.cors_allow_methods,
        "allow_headers": settings.cors_allow_headers,
    }


def get_database_config() -> dict:
    """Retorna a configuração do banco de dados."""
    return {
        "url": settings.database_url,
        "echo": settings.database_echo,
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
    }


def get_kafka_config() -> dict:
    """Retorna a configuração do Kafka."""
    return {
        "bootstrap_servers": settings.kafka_bootstrap_servers,
        "group_id": settings.kafka_group_id,
        "auto_offset_reset": settings.kafka_auto_offset_reset,
        "topics": {
            "pedido_criado": settings.kafka_topic_pedido_criado,
            "pagamento_processado": settings.kafka_topic_pagamento_processado,
            "pedido_atualizado": settings.kafka_topic_pedido_atualizado,
        },
    }


def get_app_info() -> dict:
    """Retorna informações básicas da aplicação."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "debug": settings.debug,
    }


def is_development() -> bool:
    """Verifica se a aplicação está em modo de desenvolvimento."""
    return os.getenv("ENVIRONMENT", "development").lower() == "development"


def is_production() -> bool:
    """Verifica se a aplicação está em modo de produção."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def is_testing() -> bool:
    """Verifica se a aplicação está em modo de teste."""
    return os.getenv("ENVIRONMENT", "development").lower() == "test"
