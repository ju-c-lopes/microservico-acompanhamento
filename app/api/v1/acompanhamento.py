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
                                                EventoPagamentoRequest,
                                                EventoPedidoRequest,
                                                FilaPedidosResponse,
                                                HealthResponse,
                                                SuccessResponse)

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


@router.post("/evento-pedido", response_model=SuccessResponse)
async def processar_evento_pedido(
    evento: EventoPedidoRequest,
    service: AcompanhamentoService = Depends(get_acompanhamento_service),
):
    """
    Processa evento de pedido recebido via Kafka.

    Este endpoint é chamado quando um novo pedido é criado no microserviço
    de pedidos e precisa ser registrado para acompanhamento.

    Args:
        evento: Dados do evento de pedido

    Returns:
        SuccessResponse: Confirmação do processamento

    Raises:
        400: Dados do evento inválidos
        409: Pedido já existe
        500: Erro interno do servidor
    """
    try:
        # Converte EventoPedidoRequest para EventoPedido (domain model)
        from app.models.events import EventoPedido
        from app.models.events import ItemPedido as ItemPedidoEvent

        evento_domain = EventoPedido(
            id_pedido=evento.id_pedido,
            cpf_cliente=evento.cpf_cliente,
            itens=[
                ItemPedidoEvent(id_produto=item.id_produto, quantidade=item.quantidade)
                for item in evento.itens
            ],
            total_pedido=evento.total_pedido,
            tempo_estimado=evento.tempo_estimado,
            status=evento.status,
            criado_em=evento.criado_em,
        )

        acompanhamento = await service.processar_evento_pedido(evento_domain)

        return SuccessResponse(
            message=f"Evento de pedido {evento.id_pedido} processado com sucesso",
            data={
                "id_pedido": acompanhamento.id_pedido,
                "status": acompanhamento.status.value,
                "criado_em": acompanhamento.atualizado_em.isoformat(),
            },
        )

    except ValueError as e:
        if "já existe" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar evento de pedido: {str(e)}",
        )


@router.post("/evento-pagamento", response_model=SuccessResponse)
async def processar_evento_pagamento(
    evento: EventoPagamentoRequest,
    service: AcompanhamentoService = Depends(get_acompanhamento_service),
):
    """
    Processa evento de pagamento recebido via Kafka.

    Este endpoint é chamado quando há mudanças no status de pagamento
    de um pedido e precisa atualizar o acompanhamento.

    Args:
        evento: Dados do evento de pagamento

    Returns:
        SuccessResponse: Confirmação do processamento

    Raises:
        400: Dados do evento inválidos
        404: Pedido não encontrado
        500: Erro interno do servidor
    """
    try:
        # Converte EventoPagamentoRequest para EventoPagamento (domain model)
        from app.models.events import EventoPagamento

        evento_domain = EventoPagamento(
            id_pagamento=evento.id_pagamento,
            id_pedido=evento.id_pedido,
            status=evento.status,
            criado_em=evento.criado_em,
        )

        acompanhamento = await service.processar_evento_pagamento(evento_domain)

        return SuccessResponse(
            message=f"Evento de pagamento para pedido {evento.id_pedido} processado com sucesso",
            data={
                "id_pedido": acompanhamento.id_pedido,
                "status_pagamento": acompanhamento.status_pagamento.value,
                "atualizado_em": acompanhamento.atualizado_em.isoformat(),
            },
        )

    except ValueError as e:
        if "não encontrado" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar evento de pagamento: {str(e)}",
        )
