from datetime import datetime
from typing import List, Optional

from app.domain.order_state import (OrderStateManager, StatusPagamento,
                                    StatusPedido, get_estimated_time_minutes)
from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido)


class AcompanhamentoService:
    """Serviço de domínio para lógicas de negócio do acompanhamento"""

    def __init__(self, repository):
        self.repository = repository

    async def processar_evento_pedido(self, evento: EventoPedido) -> Acompanhamento:
        """
        Processa evento de criação de pedido e cria acompanhamento
        """
        # Verifica se já existe acompanhamento para este pedido
        existing = await self.repository.buscar_por_id_pedido(evento.id_pedido)
        if existing:
            return existing

        # Cria novo acompanhamento
        acompanhamento = Acompanhamento(
            id_pedido=evento.id_pedido,
            cpf_cliente=evento.cpf_cliente,
            status=StatusPedido.RECEBIDO,
            status_pagamento=StatusPagamento.PENDENTE,
            itens=evento.itens,
            tempo_estimado=evento.tempo_estimado
            or self.calcular_tempo_estimado_por_itens(evento.itens),
            atualizado_em=datetime.now(),
        )

        return await self.repository.criar(acompanhamento)

    async def processar_evento_pagamento(
        self, evento: EventoPagamento
    ) -> Optional[Acompanhamento]:
        """
        Processa evento de pagamento e atualiza status do acompanhamento
        """
        acompanhamento = await self.repository.buscar_por_id_pedido(evento.id_pedido)
        if not acompanhamento:
            # Se não existe acompanhamento, não podemos processar
            return None

        # Atualiza status do pagamento
        acompanhamento.status_pagamento = evento.status
        acompanhamento.atualizado_em = datetime.now()

        # Se pagamento foi aprovado e pedido está recebido, muda para preparação
        if (
            evento.status == StatusPagamento.PAGO
            and acompanhamento.status == StatusPedido.RECEBIDO
        ):
            acompanhamento.status = StatusPedido.EM_PREPARACAO

        return await self.repository.atualizar(acompanhamento)

    async def atualizar_status_pedido(
        self, id_pedido: int, novo_status: StatusPedido
    ) -> Acompanhamento:
        """
        Atualiza status do pedido (usado pela cozinha)
        """
        acompanhamento = await self.repository.buscar_por_id_pedido(id_pedido)
        if not acompanhamento:
            raise ValueError(f"Acompanhamento não encontrado para pedido {id_pedido}")

        # Valida transição de estado
        current_status = StatusPedido(acompanhamento.status)
        if not OrderStateManager.can_transition(current_status, novo_status):
            raise ValueError(
                f"Transição inválida de '{current_status}' para '{novo_status}'"
            )

        # Atualiza status
        acompanhamento.status = novo_status
        acompanhamento.atualizado_em = datetime.now()

        return await self.repository.atualizar(acompanhamento)

    async def buscar_fila_pedidos(self) -> List[Acompanhamento]:
        """
        Busca pedidos na fila de pedidos (Em preparação e Pronto)
        Linguagem ubíqua: fila de pedidos em vez de fila de produção
        """
        return await self.repository.buscar_por_status(
            [StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO]
        )

    def calcular_tempo_estimado(self, acompanhamento: Acompanhamento) -> str:
        """
        Calcula tempo estimado baseado no status atual
        """
        status = StatusPedido(acompanhamento.status)
        tempo_minutos = get_estimated_time_minutes(status)

        # Converte para formato HH:MM:SS
        horas = tempo_minutos // 60
        minutos = tempo_minutos % 60
        return f"{horas:02d}:{minutos:02d}:00"

    def calcular_tempo_estimado_por_itens(self, itens: List) -> str:
        """
        Calcula tempo estimado baseado nos itens do pedido.

        Considera categorias vindas do microserviço de pedidos (em maiúsculas):
        - LANCHE: +5 minutos por quantidade
        - ACOMPANHAMENTO: +2 minutos por quantidade
        - BEBIDA: +1 minuto por quantidade
        - SOBREMESA: +3 minutos por quantidade

        Exemplo: 2 lanches = 5 * 2 = 10 minutos adicionais
        """
        tempo_base = 15  # 15 minutos base
        tempo_adicional = 0

        for item in itens:
            categoria = None
            quantidade = 1  # Padrão caso não seja informada

            # Tenta obter categoria e quantidade de diferentes formas possíveis
            if hasattr(item, "categoria"):
                categoria = getattr(item, "categoria", "").upper()
                quantidade = getattr(item, "quantidade", 1)
            elif hasattr(item, "category"):
                categoria = getattr(item, "category", "").upper()
                quantidade = getattr(item, "quantidade", getattr(item, "quality", 1))
            elif isinstance(item, dict):
                categoria_raw = item.get("categoria", item.get("category", ""))
                categoria = (categoria_raw or "").upper()
                quantidade = item.get("quantidade", item.get("quantity", 1))
            else:
                # Para objetos que não têm categoria mas podem ter quantidade
                if hasattr(item, "quantidade"):
                    quantidade = getattr(item, "quantidade", 1)
                elif hasattr(item, "quantity"):
                    quantidade = getattr(item, "quantity", 1)

            # Calcula tempo adicional baseado na categoria e quantidade
            if categoria == "LANCHE":
                tempo_adicional += 5 * quantidade
            elif categoria == "ACOMPANHAMENTO":
                tempo_adicional += 2 * quantidade
            elif categoria == "SOBREMESA":
                tempo_adicional += 3 * quantidade
            elif categoria == "BEBIDA":
                tempo_adicional += 1 * quantidade
            else:
                # Categoria desconhecida ou não informada
                tempo_adicional += 3 * quantidade  # Tempo padrão

        tempo_total = tempo_base + tempo_adicional

        # Converte para formato HH:MM:SS
        horas = tempo_total // 60
        minutos = tempo_total % 60
        return f"{horas:02d}:{minutos:02d}:00"

    async def buscar_pedidos_cliente(self, cpf_cliente: str) -> List[Acompanhamento]:
        """
        Busca todos os pedidos de um cliente específico
        """
        return await self.repository.buscar_por_cpf_cliente(cpf_cliente)

    def _deve_notificar_cliente(self, novo_status: StatusPedido) -> bool:
        """
        Determina se cliente deve ser notificado sobre mudança de status
        """
        # Notifica quando pedido fica pronto ou é finalizado
        return novo_status in [StatusPedido.PRONTO, StatusPedido.FINALIZADO]
