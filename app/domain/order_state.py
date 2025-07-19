from enum import Enum


class StatusPedido(str, Enum):
    """Estados possíveis de um pedido no sistema de acompanhamento"""

    RECEBIDO = "Recebido"
    EM_PREPARACAO = "Em preparação"
    PRONTO = "Pronto"
    FINALIZADO = "Finalizado"


class StatusPagamento(str, Enum):
    """Estados possíveis de pagamento"""

    PENDENTE = "pendente"
    PAGO = "pago"
    FALHOU = "falhou"


class OrderStateManager:
    """Gerenciador de transições de estado do pedido"""

    # Mapeamento de transições válidas
    VALID_TRANSITIONS = {
        StatusPedido.RECEBIDO: [StatusPedido.EM_PREPARACAO],
        StatusPedido.EM_PREPARACAO: [StatusPedido.PRONTO],
        StatusPedido.PRONTO: [StatusPedido.FINALIZADO],
        StatusPedido.FINALIZADO: [],  # Estado final
    }

    @classmethod
    def can_transition(
        cls, current_status: StatusPedido, new_status: StatusPedido
    ) -> bool:
        """Verifica se uma transição de estado é válida"""
        if current_status not in cls.VALID_TRANSITIONS:
            return False
        return new_status in cls.VALID_TRANSITIONS[current_status]

    @classmethod
    def get_next_valid_states(cls, current_status: StatusPedido) -> list[StatusPedido]:
        """Retorna os próximos estados válidos para o estado atual"""
        return cls.VALID_TRANSITIONS.get(current_status, [])

    @classmethod
    def should_update_from_payment(cls, payment_status: StatusPagamento) -> bool:
        """Determina se o status do pedido deve ser atualizado baseado no pagamento"""
        return payment_status == StatusPagamento.PAGO


def get_estimated_time_minutes(status: StatusPedido) -> int:
    """Retorna tempo estimado em minutos para cada estado"""
    time_mapping = {
        StatusPedido.RECEBIDO: 5,  # 5 min aguardando pagamento
        StatusPedido.EM_PREPARACAO: 15,  # 15 min preparando
        StatusPedido.PRONTO: 10,  # 10 min aguardando retirada
        StatusPedido.FINALIZADO: 0,  # Finalizado
    }
    return time_mapping.get(status, 0)
