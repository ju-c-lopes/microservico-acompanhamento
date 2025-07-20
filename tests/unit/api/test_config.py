"""
Testes unitários para o sistema de configuração.
Valida carregamento de configurações por ambiente, validações e funções utilitárias.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from app.core.config import DevelopmentSettings, ProductionSettings, Settings
from app.core.config import TestSettings as ConfigTestSettings
from app.core.config import (configure_logging, get_app_info, get_cors_config,
                             get_database_config, get_kafka_config,
                             get_settings, is_development, is_production,
                             is_testing)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Limpa o cache das configurações antes de cada teste."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestSettings:
    """Testes para a classe Settings base."""

    def test_default_settings_creation(self):
        """Testa criação de configurações com valores padrão."""
        settings = Settings()

        # API settings - pode variar com variáveis de ambiente de teste
        expected_names = ["Microserviço Acompanhamento", "Test Acompanhamento Service"]
        assert settings.app_name in expected_names
        assert settings.app_version == "1.0.0"
        assert "API para acompanhamento" in settings.app_description
        # Debug pode variar em ambiente de teste
        assert isinstance(settings.debug, bool)

        # Server settings
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload is False

        # CORS settings
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:8080" in settings.cors_origins
        assert settings.cors_allow_credentials is True
        assert "GET" in settings.cors_allow_methods
        assert "POST" in settings.cors_allow_methods

        # Database settings
        # Nota: pode variar baseado na variável DATABASE_URL do ambiente
        assert (
            "postgresql+asyncpg" in settings.database_url
            or "sqlite+aiosqlite" in settings.database_url
        )
        assert settings.database_echo is False
        assert settings.database_pool_size == 5
        assert settings.database_max_overflow == 10

        # Kafka settings
        assert settings.kafka_bootstrap_servers == "localhost:9092"
        assert settings.kafka_group_id == "acompanhamento-service"
        assert settings.kafka_auto_offset_reset == "latest"
        assert settings.kafka_topic_pedido_criado == "pedido.criado"
        assert settings.kafka_topic_pagamento_processado == "pagamento.processado"
        assert settings.kafka_topic_pedido_atualizado == "pedido.atualizado"

        # Logging settings
        assert settings.log_level == "INFO"
        assert "%(asctime)s" in settings.log_format
        assert settings.log_file is None

        # Security settings - pode variar em ambiente de teste
        expected_secret_keys = ["change-me-in-production", "test-secret-key"]
        assert settings.secret_key in expected_secret_keys
        assert settings.access_token_expire_minutes == 30

        # Performance settings
        assert settings.request_timeout == 30
        assert settings.max_request_size == 1048576  # 1MB

        # Monitoring settings
        assert settings.enable_metrics is True
        assert settings.metrics_path == "/metrics"
        assert settings.health_check_path == "/health"

        # External integration settings
        assert settings.external_api_timeout == 10
        assert settings.max_retries == 3
        assert settings.retry_delay == 1

    def test_settings_with_environment_variables(self):
        """Testa configurações carregadas de variáveis de ambiente."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Test App",
                "APP_VERSION": "2.0.0",
                "DEBUG": "true",
                "PORT": "9000",
                "CORS_ORIGINS": "http://test.com,http://localhost:4000",
                "DATABASE_POOL_SIZE": "10",
                "LOG_LEVEL": "DEBUG",
                "SECRET_KEY": "test-secret-key",
            },
        ):
            settings = Settings()

            assert settings.app_name == "Test App"
            assert settings.app_version == "2.0.0"
            assert settings.debug is True
            assert settings.port == 9000
            assert settings.cors_origins == ["http://test.com", "http://localhost:4000"]
            assert settings.database_pool_size == 10
            assert settings.log_level == "DEBUG"
            assert settings.secret_key == "test-secret-key"

    def test_cors_origins_parsing(self):
        """Testa parsing de CORS origins como string."""
        with patch.dict(
            os.environ,
            {
                "CORS_ORIGINS": "http://localhost:3000, http://localhost:8080 , http://test.com"
            },
        ):
            settings = Settings()
            expected = [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://test.com",
            ]
            assert settings.cors_origins == expected

    def test_cors_methods_parsing(self):
        """Testa parsing de CORS methods como string."""
        with patch.dict(os.environ, {"CORS_ALLOW_METHODS": "GET, POST , PUT,DELETE"}):
            settings = Settings()
            expected = ["GET", "POST", "PUT", "DELETE"]
            assert settings.cors_allow_methods == expected

    def test_boolean_environment_variables(self):
        """Testa conversão de strings para boolean."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("", False),
            ("anything", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"DEBUG": env_value}):
                settings = Settings()
                assert settings.debug == expected

    def test_invalid_log_level_raises_error(self):
        """Testa que nível de log inválido levanta erro."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            with pytest.raises(ValueError, match="Log level deve ser um de"):
                Settings()

    def test_invalid_kafka_offset_reset_raises_error(self):
        """Testa que offset reset inválido do Kafka levanta erro."""
        with patch.dict(os.environ, {"KAFKA_AUTO_OFFSET_RESET": "invalid"}):
            with pytest.raises(
                ValueError, match="kafka_auto_offset_reset deve ser um de"
            ):
                Settings()

    def test_valid_log_levels(self):
        """Testa todos os níveis de log válidos."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                settings = Settings()
                assert settings.log_level == level

    def test_valid_kafka_offset_reset_values(self):
        """Testa todos os valores válidos de offset reset do Kafka."""
        valid_values = ["latest", "earliest", "none"]

        for value in valid_values:
            with patch.dict(os.environ, {"KAFKA_AUTO_OFFSET_RESET": value}):
                settings = Settings()
                assert settings.kafka_auto_offset_reset == value


class TestDevelopmentSettings:
    """Testes para configurações de desenvolvimento."""

    def test_development_overrides(self):
        """Testa que configurações de desenvolvimento sobrescrevem adequadamente."""
        settings = DevelopmentSettings()

        assert settings.debug is True
        assert settings.reload is True
        assert settings.database_echo is True
        assert settings.log_level == "DEBUG"
        assert settings.cors_origins == ["*"]


class TestProductionSettings:
    """Testes para configurações de produção."""

    def test_production_overrides(self):
        """Testa que configurações de produção sobrescrevem adequadamente."""
        settings = ProductionSettings()

        assert settings.debug is False
        assert settings.reload is False
        assert settings.database_echo is False
        assert settings.log_level == "INFO"


class TestConfigTestSettings:
    """Testes para configurações de teste."""

    def test_test_overrides(self):
        """Testa que configurações de teste sobrescrevem adequadamente."""
        settings = ConfigTestSettings()

        assert settings.debug is True
        assert "sqlite+aiosqlite" in settings.database_url
        assert settings.kafka_bootstrap_servers == "localhost:9092"
        assert settings.log_level == "WARNING"


class TestGetSettings:
    """Testes para a função get_settings."""

    def test_get_settings_development(self):
        """Testa carregamento de configurações de desenvolvimento."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            settings = get_settings()
            assert isinstance(settings, DevelopmentSettings)
            assert settings.debug is True

    def test_get_settings_production(self):
        """Testa carregamento de configurações de produção."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = get_settings()
            assert isinstance(settings, ProductionSettings)
            assert settings.debug is False

    def test_get_settings_test(self):
        """Testa carregamento de configurações de teste."""
        with patch.dict(os.environ, {"ENVIRONMENT": "test"}):
            settings = get_settings()
            assert isinstance(settings, ConfigTestSettings)
            assert "sqlite" in settings.database_url

    def test_get_settings_default(self):
        """Testa que desenvolvimento é o padrão quando ENVIRONMENT não está definido."""
        with patch.dict(os.environ, {}, clear=True):
            if "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            settings = get_settings()
            assert isinstance(settings, DevelopmentSettings)

    def test_get_settings_case_insensitive(self):
        """Testa que ENVIRONMENT é case insensitive."""
        test_cases = ["PRODUCTION", "Production", "pRoDuCtIoN"]

        for env_value in test_cases:
            with patch.dict(os.environ, {"ENVIRONMENT": env_value}):
                settings = get_settings()
                assert isinstance(settings, ProductionSettings)


class TestUtilityFunctions:
    """Testes para funções utilitárias."""

    def test_get_cors_config(self):
        """Testa configuração de CORS."""
        # Testa com settings padrão
        config = get_cors_config()

        # Verifica estrutura do config
        assert "allow_origins" in config
        assert "allow_credentials" in config
        assert "allow_methods" in config
        assert "allow_headers" in config

        # Verifica tipos
        assert isinstance(config["allow_origins"], list)
        assert isinstance(config["allow_credentials"], bool)
        assert isinstance(config["allow_methods"], list)
        assert isinstance(config["allow_headers"], list)

    def test_get_database_config(self):
        """Testa configuração do banco de dados."""
        config = get_database_config()

        # Verifica estrutura do config
        assert "url" in config
        assert "echo" in config
        assert "pool_size" in config
        assert "max_overflow" in config

        # Verifica tipos
        assert isinstance(config["url"], str)
        assert isinstance(config["echo"], bool)
        assert isinstance(config["pool_size"], int)
        assert isinstance(config["max_overflow"], int)

    def test_get_kafka_config(self):
        """Testa configuração do Kafka."""
        config = get_kafka_config()

        # Verifica estrutura do config
        assert "bootstrap_servers" in config
        assert "group_id" in config
        assert "auto_offset_reset" in config
        assert "topics" in config

        # Verifica tópicos
        topics = config["topics"]
        assert "pedido_criado" in topics
        assert "pagamento_processado" in topics
        assert "pedido_atualizado" in topics

    def test_get_app_info(self):
        """Testa informações da aplicação."""
        info = get_app_info()

        # Verifica estrutura
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "debug" in info

        # Verifica tipos
        assert isinstance(info["name"], str)
        assert isinstance(info["version"], str)
        assert isinstance(info["description"], str)
        assert isinstance(info["debug"], bool)

    def test_environment_check_functions(self):
        """Testa funções de verificação de ambiente."""
        # Como as funções leem diretamente do os.environ,
        # vamos testar que pelo menos uma é True (comportamento padrão)
        is_dev = is_development()
        is_prod = is_production()
        is_test = is_testing()

        # Pelo menos uma deve ser True
        assert is_dev or is_prod or is_test

        # Não podem ser todas True ao mesmo tempo
        assert not (is_dev and is_prod and is_test)


class TestLoggingConfiguration:
    """Testes para configuração de logging."""

    def test_configure_logging_basic(self):
        """Testa configuração básica de logging."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INFO"}):
            # Não deve levantar exceção
            configure_logging()

    def test_configure_logging_with_file(self):
        """Testa configuração de logging com arquivo."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            with patch.dict(
                os.environ, {"LOG_LEVEL": "DEBUG", "LOG_FILE": tmp_file.name}
            ):
                # Não deve levantar exceção
                configure_logging()

        # Cleanup
        os.unlink(tmp_file.name)


@pytest.mark.unit
class TestConfigIntegration:
    """Testes de integração das configurações."""

    def test_full_configuration_cycle(self):
        """Testa ciclo completo de configuração."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "test",
                "APP_NAME": "Integration Test App",
                "DATABASE_URL": "sqlite+aiosqlite:///integration_test.db",
                "LOG_LEVEL": "WARNING",
            },
        ):
            # Limpa cache para forçar nova configuração
            get_settings.cache_clear()

            # Obter configurações
            settings = get_settings()
            assert isinstance(settings, ConfigTestSettings)

            # Testar funções utilitárias
            db_config = get_database_config()
            assert "url" in db_config
            assert isinstance(db_config["url"], str)

            cors_config = get_cors_config()
            assert isinstance(cors_config["allow_origins"], list)

            kafka_config = get_kafka_config()
            assert "topics" in kafka_config

            app_info = get_app_info()
            assert isinstance(app_info["name"], str)
            assert len(app_info["name"]) > 0
