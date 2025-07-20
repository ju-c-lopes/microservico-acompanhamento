"""
Endpoints REST para acompanhamento de pedidos.
Equivalente ao acompanhamento_handler.go do Golang, mas adaptado para arquitetura de microsserviços.

Estrutura de rotas:
- /acompanhamento/{id_pedido} - Buscar acompanhamento
- /acompanhamento/{id_pedido}/status - Atualizar status (cozinha)
- /acompanhamento/fila/pedidos - Fila da cozinha
- /acompanhamento/cliente/{cpf} - Histórico do cliente
- /acompanhamento/health - Health check
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_acompanhamento_service
from app.domain.acompanhamento_service import AcompanhamentoService
from app.schemas.acompanhamento_schemas import (AcompanhamentoResponse,
                                                AcompanhamentoResumoResponse,
                                                AtualizarStatusRequest,
                                                FilaPedidosResponse,
                                                HealthResponse)

# Router com prefixo /acompanhamento (sem /api/v1 conforme sugerido)
router = APIRouter(prefix="/acompanhamento", tags=["acompanhamento"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check do microserviço de acompanhamento.
    Usado para monitoramento e verificação de disponibilidade.
    """
    from datetime import datetime

    return HealthResponse(
        status="healthy",
        service="acompanhamento",
        timestamp=datetime.now(),
        version="1.0.0",
    )


@router.get("/{id_pedido}", response_model=AcompanhamentoResponse)
async def buscar_acompanhamento(
    id_pedido: int, service: AcompanhamentoService = Depends(get_acompanhamento_service)
):
    """
    Busca acompanhamento de um pedido específico.

    Usado principalmente pelo cliente para verificar o status do seu pedido.
    Equivalente ao BuscarAcompanhamento do Golang.

    Args:
        id_pedido: ID do pedido a ser consultado

    Returns:
        AcompanhamentoResponse: Dados completos do acompanhamento

    Raises:
        404: Acompanhamento não encontrado
        400: ID do pedido inválido
    """
    try:
        acompanhamento = await service.repository.buscar_por_id_pedido(id_pedido)
        if not acompanhamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Acompanhamento não encontrado para pedido {id_pedido}",
            )
        return acompanhamento
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id_pedido}/status", response_model=AcompanhamentoResponse)
async def atualizar_status_pedido(
    id_pedido: int,
    request: AtualizarStatusRequest,
    service: AcompanhamentoService = Depends(get_acompanhamento_service),
):
    """
    Atualiza status de um pedido (usado pela cozinha).

    Permite que a cozinha atualize o progresso do pedido:
    - RECEBIDO -> EM_PREPARACAO (quando começar a preparar)
    - EM_PREPARACAO -> PRONTO (quando terminar)
    - PRONTO -> FINALIZADO (quando cliente retirar)

    Equivalente ao AtualizarStatusPedido do Golang.

    Args:
        id_pedido: ID do pedido a ser atualizado
        request: Novo status a ser aplicado

    Returns:
        AcompanhamentoResponse: Dados atualizados do acompanhamento

    Raises:
        404: Acompanhamento não encontrado
        400: Transição de status inválida
    """
    try:
        acompanhamento = await service.atualizar_status_pedido(
            id_pedido, request.status
        )
        return acompanhamento
    except ValueError as e:
        if "não encontrado" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/fila/pedidos", response_model=FilaPedidosResponse)
async def buscar_fila_pedidos(
    service: AcompanhamentoService = Depends(get_acompanhamento_service),
):
    """
    Busca fila de pedidos para a cozinha.

    Retorna pedidos que estão EM_PREPARACAO ou PRONTO, ou seja,
    todos os pedidos que precisam de atenção da cozinha.

    Usado no monitor da cozinha para visualizar a fila de trabalho.

    Returns:
        FilaPedidosResponse: Lista de pedidos na fila com resumo

    Raises:
        500: Erro interno do servidor
    """
    try:
        pedidos = await service.buscar_fila_pedidos()
        return FilaPedidosResponse(
            pedidos=[
                AcompanhamentoResumoResponse(
                    id_pedido=p.id_pedido,
                    cpf_cliente=p.cpf_cliente,
                    status=p.status,
                    tempo_estimado=p.tempo_estimado,
                    atualizado_em=p.atualizado_em,
                )
                for p in pedidos
            ],
            total=len(pedidos),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar fila de pedidos: {str(e)}",
        )


@router.get("/cliente/{cpf}", response_model=List[AcompanhamentoResponse])
async def buscar_pedidos_cliente(
    cpf: str, service: AcompanhamentoService = Depends(get_acompanhamento_service)
):
    """
    Busca histórico de pedidos de um cliente específico.

    Usado para:
    - Campanhas promocionais baseadas no histórico
    - Atendimento ao cliente
    - Análise de comportamento de compra

    Args:
        cpf: CPF do cliente (com ou sem formatação)

    Returns:
        List[AcompanhamentoResponse]: Lista de todos os pedidos do cliente

    Raises:
        400: CPF inválido
        500: Erro interno do servidor
    """
    try:
        # Validação básica do CPF (apenas dígitos)
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF deve conter 11 dígitos",
            )

        pedidos = await service.buscar_pedidos_cliente(cpf_limpo)
        return pedidos
    except HTTPException:
        raise  # Re-raise HTTPException
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pedidos do cliente: {str(e)}",
        )
