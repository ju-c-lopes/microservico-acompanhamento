from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.order_state import StatusPedido
from app.models.acompanhamento import Acompanhamento


class AcompanhamentoRepositoryInterface(ABC):
    """Interface do repositório de acompanhamento"""

    @abstractmethod
    async def criar(self, acompanhamento: Acompanhamento) -> Acompanhamento:
        pass

    @abstractmethod
    async def buscar_por_id(self, id: int) -> Optional[Acompanhamento]:
        pass

    @abstractmethod
    async def buscar_por_id_pedido(self, id_pedido: int) -> Optional[Acompanhamento]:
        pass

    @abstractmethod
    async def buscar_por_cpf_cliente(self, cpf_cliente: str) -> List[Acompanhamento]:
        pass

    @abstractmethod
    async def buscar_por_status(
        self, status_list: List[StatusPedido]
    ) -> List[Acompanhamento]:
        pass

    @abstractmethod
    async def atualizar(self, acompanhamento: Acompanhamento) -> Acompanhamento:
        pass

    @abstractmethod
    async def listar_todos(
        self, skip: int = 0, limit: int = 100
    ) -> List[Acompanhamento]:
        pass


class AcompanhamentoRepository(AcompanhamentoRepositoryInterface):
    """Implementação do repositório de acompanhamento usando SQLAlchemy"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def criar(self, acompanhamento: Acompanhamento) -> Acompanhamento:
        """Cria um novo acompanhamento no banco de dados"""
        from app.db.base import Acompanhamento as AcompanhamentoModel
        from app.db.base import ItemPedido as ItemPedidoModel

        db_acompanhamento = AcompanhamentoModel(
            id_pedido=acompanhamento.id_pedido,
            cpf_cliente=acompanhamento.cpf_cliente,
            status=acompanhamento.status,
            status_pagamento=acompanhamento.status_pagamento,
            tempo_estimado=acompanhamento.tempo_estimado,
            atualizado_em=acompanhamento.atualizado_em,
        )

        self.db.add(db_acompanhamento)
        await self.db.commit()
        await self.db.refresh(db_acompanhamento)

        # Criar itens do pedido
        for item in acompanhamento.itens:
            db_item = ItemPedidoModel(
                id_produto=item.id_produto,
                id_pedido=acompanhamento.id_pedido,
                nome_produto=f"Produto {item.id_produto}",
                quantidade=item.quantidade,
            )
            self.db.add(db_item)

        await self.db.commit()
        return self._to_domain_model(db_acompanhamento)

    async def buscar_por_id(self, id: int) -> Optional[Acompanhamento]:
        """Busca acompanhamento por ID"""
        from app.models.events import AcompanhamentoModel

        result = await self.db.execute(
            select(AcompanhamentoModel).where(AcompanhamentoModel.id == id)
        )
        db_acompanhamento = result.scalar_one_or_none()

        return self._to_domain_model(db_acompanhamento) if db_acompanhamento else None

    async def buscar_por_id_pedido(self, id_pedido: int) -> Optional[Acompanhamento]:
        """Busca acompanhamento por ID do pedido"""
        from app.models.events import AcompanhamentoModel

        result = await self.db.execute(
            select(AcompanhamentoModel).where(
                AcompanhamentoModel.id_pedido == id_pedido
            )
        )
        db_acompanhamento = result.scalar_one_or_none()

        return self._to_domain_model(db_acompanhamento) if db_acompanhamento else None

    async def buscar_por_cpf_cliente(self, cpf_cliente: str) -> List[Acompanhamento]:
        """Busca acompanhamentos por CPF do cliente"""
        from app.models.events import AcompanhamentoModel

        result = await self.db.execute(
            select(AcompanhamentoModel)
            .where(AcompanhamentoModel.cpf_cliente == cpf_cliente)
            .order_by(AcompanhamentoModel.atualizado_em.desc())
        )
        db_acompanhamentos = result.scalars().all()

        return [self._to_domain_model(db_acomp) for db_acomp in db_acompanhamentos]

    async def buscar_por_status(
        self, status_list: List[StatusPedido]
    ) -> List[Acompanhamento]:
        """Busca acompanhamentos por lista de status"""
        from app.models.events import AcompanhamentoModel

        status_strings = [status.value for status in status_list]

        result = await self.db.execute(
            select(AcompanhamentoModel)
            .where(AcompanhamentoModel.status.in_(status_strings))
            .order_by(AcompanhamentoModel.atualizado_em.asc())
        )
        db_acompanhamentos = result.scalars().all()

        return [self._to_domain_model(db_acomp) for db_acomp in db_acompanhamentos]

    async def atualizar(self, acompanhamento: Acompanhamento) -> Acompanhamento:
        """Atualiza um acompanhamento existente"""
        from app.models.events import AcompanhamentoModel

        # Busca o registro existente
        result = await self.db.execute(
            select(AcompanhamentoModel).where(
                AcompanhamentoModel.id_pedido == acompanhamento.id_pedido
            )
        )
        db_acompanhamento = result.scalar_one_or_none()

        if not db_acompanhamento:
            raise ValueError(
                f"Acompanhamento não encontrado para pedido {acompanhamento.id_pedido}"
            )

        # Atualiza os campos
        db_acompanhamento.status = acompanhamento.status
        db_acompanhamento.status_pagamento = acompanhamento.status_pagamento
        db_acompanhamento.itens = (
            acompanhamento.itens.model_dump()
            if hasattr(acompanhamento.itens, "model_dump")
            else [item.model_dump() for item in acompanhamento.itens]
        )
        db_acompanhamento.tempo_estimado = acompanhamento.tempo_estimado
        db_acompanhamento.atualizado_em = acompanhamento.atualizado_em

        await self.db.commit()
        await self.db.refresh(db_acompanhamento)

        return self._to_domain_model(db_acompanhamento)

    async def listar_todos(
        self, skip: int = 0, limit: int = 100
    ) -> List[Acompanhamento]:
        """Lista todos os acompanhamentos com paginação"""
        from app.models.events import AcompanhamentoModel

        result = await self.db.execute(
            select(AcompanhamentoModel)
            .order_by(AcompanhamentoModel.atualizado_em.desc())
            .offset(skip)
            .limit(limit)
        )
        db_acompanhamentos = result.scalars().all()

        return [self._to_domain_model(db_acomp) for db_acomp in db_acompanhamentos]

    def _to_domain_model(self, db_acompanhamento) -> Acompanhamento:
        """Converte modelo do banco para modelo de domínio"""
        from app.models.acompanhamento import ItemPedido

        # Converte itens do JSON para lista de ItemPedido
        itens = []
        if db_acompanhamento.itens:
            for item_data in db_acompanhamento.itens:
                if isinstance(item_data, dict):
                    itens.append(ItemPedido(**item_data))
                else:
                    itens.append(item_data)

        return Acompanhamento(
            id_pedido=db_acompanhamento.id_pedido,
            cpf_cliente=db_acompanhamento.cpf_cliente,
            status=db_acompanhamento.status,
            status_pagamento=db_acompanhamento.status_pagamento,
            itens=itens,
            tempo_estimado=db_acompanhamento.tempo_estimado,
            atualizado_em=db_acompanhamento.atualizado_em,
        )
