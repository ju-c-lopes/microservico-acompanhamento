"""
Dependências do FastAPI para injeção de dependências.
Equivalente ao bootstrap/app.go e repositories.go do Golang.

Inclui:
- Injeção de dependências para repository e service
- Context managers para tratamento de exceções
- Utilities para validação de entrada
"""

import re
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (AcompanhamentoException,
                                 DatabaseConnectionError, InvalidCPFError,
                                 create_error_response,
                                 get_http_status_for_exception)
from app.db.session import async_session
from app.domain.acompanhamento_service import AcompanhamentoService
from app.repository.acompanhamento_repository import AcompanhamentoRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obter sessão do banco de dados.
    Inclui tratamento de erros de conexão.
    """
    try:
        async with async_session() as session:
            yield session
    except SQLAlchemyError as e:
        raise DatabaseConnectionError(
            operation="session_creation", original_error=str(e)
        ) from e


def get_acompanhamento_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AcompanhamentoRepository:
    """
    Cria uma instância do repositório de acompanhamento.
    Equivalente ao NewAcompanhamentoMySQLRepository do Golang.

    Args:
        session: Sessão do banco de dados injetada

    Returns:
        AcompanhamentoRepository: Instância do repositório configurada
    """
    return AcompanhamentoRepository(session=session)


def get_acompanhamento_service(
    repository: AcompanhamentoRepository = Depends(get_acompanhamento_repository),
) -> AcompanhamentoService:
    """
    Cria uma instância do serviço de acompanhamento com injeção de dependências.
    Equivalente ao NewAcompanhamentoUseCase do Golang.

    Args:
        repository: Repositório de acompanhamento injetado

    Returns:
        AcompanhamentoService: Instância do serviço configurada
    """
    return AcompanhamentoService(repository)


@asynccontextmanager
async def handle_service_exceptions():
    """
    Context manager para tratar exceções do service layer de forma padronizada.
    Converte exceções customizadas em HTTPExceptions apropriadas.

    Usage:
        async with handle_service_exceptions():
            # operações que podem gerar exceções
            result = await service.some_operation()
    """
    try:
        yield
    except AcompanhamentoException as e:
        # Exceções customizadas do domínio
        status_code = get_http_status_for_exception(e)
        error_response = create_error_response(e)
        raise HTTPException(status_code=status_code, detail=error_response) from e
    except Exception as e:
        # Outras exceções não tratadas
        raise HTTPException(
            status_code=500,
            detail={
                "detail": "Erro interno do servidor",
                "error_code": "INTERNAL_SERVER_ERROR",
                "error_type": type(e).__name__,
            },
        ) from e


def validate_cpf(cpf: str) -> str:
    """
    Valida e limpa um CPF de entrada.

    Args:
        cpf: CPF a ser validado (pode conter formatação)

    Returns:
        str: CPF limpo (apenas dígitos)

    Raises:
        InvalidCPFError: Se o CPF não for válido
    """
    # Remove formatação (pontos, hífens, espaços)
    cpf_limpo = re.sub(r"\D", "", cpf)

    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        raise InvalidCPFError(cpf)

    # Verifica se não são todos os dígitos iguais (ex: 11111111111)
    if len(set(cpf_limpo)) == 1:
        raise InvalidCPFError(cpf)

    return cpf_limpo


def validate_id_pedido(id_pedido: int) -> int:
    """
    Valida ID do pedido.

    Args:
        id_pedido: ID do pedido a ser validado

    Returns:
        int: ID validado

    Raises:
        HTTPException: Se o ID for inválido
    """
    if id_pedido <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "ID do pedido deve ser um número positivo",
                "error_code": "INVALID_ORDER_ID",
                "error_type": "ValidationError",
            },
        )

    return id_pedido


def get_validated_cpf(cpf: str) -> str:
    """
    Dependency para validação automática de CPF em endpoints.

    Args:
        cpf: CPF a ser validado

    Returns:
        str: CPF limpo e validado

    Raises:
        HTTPException: Se o CPF for inválido
    """
    try:
        return validate_cpf(cpf)
    except InvalidCPFError as e:
        status_code = get_http_status_for_exception(e)
        error_response = create_error_response(e)
        raise HTTPException(status_code=status_code, detail=error_response) from e
