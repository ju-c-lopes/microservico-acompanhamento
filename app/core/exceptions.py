"""
Exceções customizadas para o microserviço de acompanhamento.
Fornece tratamento específico de erros de domínio e facilita debugging.
"""

from typing import Optional


class AcompanhamentoException(Exception):
    """
    Exceção base para todas as exceções relacionadas ao acompanhamento.
    Todas as outras exceções customizadas devem herdar desta.
    """

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AcompanhamentoNotFound(AcompanhamentoException):
    """
    Exceção lançada quando um acompanhamento não é encontrado.
    Usada principalmente em operações de busca e atualização.
    """

    def __init__(self, id_pedido: int):
        message = f"Acompanhamento não encontrado para pedido {id_pedido}"
        super().__init__(message, "ACOMPANHAMENTO_NOT_FOUND")
        self.id_pedido = id_pedido


class InvalidStatusTransition(AcompanhamentoException):
    """
    Exceção lançada quando uma transição de status inválida é tentada.
    Garante que as regras de negócio de transição sejam respeitadas.
    """

    def __init__(self, current_status: str, new_status: str):
        message = f"Transição inválida de '{current_status}' para '{new_status}'"
        super().__init__(message, "INVALID_STATUS_TRANSITION")
        self.current_status = current_status
        self.new_status = new_status


class EventProcessingError(AcompanhamentoException):
    """
    Exceção lançada quando há erro no processamento de eventos Kafka.
    Facilita o tratamento de erros na integração entre microserviços.
    """

    def __init__(self, event_type: str, event_data: dict, original_error: str):
        message = f"Erro ao processar evento {event_type}: {original_error}"
        super().__init__(message, "EVENT_PROCESSING_ERROR")
        self.event_type = event_type
        self.event_data = event_data
        self.original_error = original_error


class InvalidCPFError(AcompanhamentoException):
    """
    Exceção lançada quando um CPF inválido é fornecido.
    Usada na validação de entrada para busca de pedidos por cliente.
    """

    def __init__(self, cpf: str):
        message = f"CPF inválido: {cpf}. CPF deve conter 11 dígitos numéricos"
        super().__init__(message, "INVALID_CPF")
        self.cpf = cpf


class DatabaseConnectionError(AcompanhamentoException):
    """
    Exceção lançada quando há problemas de conexão com o banco de dados.
    Facilita o monitoramento e troubleshooting de problemas de infraestrutura.
    """

    def __init__(self, operation: str, original_error: str):
        message = f"Erro de conexão com banco de dados durante '{operation}': {original_error}"
        super().__init__(message, "DATABASE_CONNECTION_ERROR")
        self.operation = operation
        self.original_error = original_error


class BusinessRuleViolation(AcompanhamentoException):
    """
    Exceção lançada quando uma regra de negócio é violada.
    Usada para validações específicas do domínio de acompanhamento.
    """

    def __init__(self, rule_name: str, details: str):
        message = f"Violação da regra de negócio '{rule_name}': {details}"
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
        self.rule_name = rule_name
        self.details = details


class DuplicateOrderError(AcompanhamentoException):
    """
    Exceção lançada quando se tenta criar um acompanhamento para um pedido já existente.
    Garante a integridade dos dados e evita duplicações.
    """

    def __init__(self, id_pedido: int):
        message = f"Já existe acompanhamento para o pedido {id_pedido}"
        super().__init__(message, "DUPLICATE_ORDER")
        self.id_pedido = id_pedido


# Mapeamento de exceções para códigos HTTP
EXCEPTION_HTTP_MAPPING = {
    AcompanhamentoNotFound: 404,
    InvalidStatusTransition: 400,
    InvalidCPFError: 400,
    BusinessRuleViolation: 400,
    DuplicateOrderError: 409,
    EventProcessingError: 422,
    DatabaseConnectionError: 503,
    AcompanhamentoException: 500,  # Fallback para exceções genéricas
}


def get_http_status_for_exception(exception: Exception) -> int:
    """
    Retorna o código HTTP apropriado para uma exceção.

    Args:
        exception: A exceção a ser mapeada

    Returns:
        int: Código HTTP apropriado (default: 500)
    """
    exception_type = type(exception)
    return EXCEPTION_HTTP_MAPPING.get(exception_type, 500)


def create_error_response(exception: AcompanhamentoException) -> dict:
    """
    Cria uma resposta de erro padronizada a partir de uma exceção customizada.

    Args:
        exception: A exceção customizada

    Returns:
        dict: Dicionário com dados formatados do erro
    """
    return {
        "detail": exception.message,
        "error_code": exception.error_code,
        "error_type": type(exception).__name__,
    }
