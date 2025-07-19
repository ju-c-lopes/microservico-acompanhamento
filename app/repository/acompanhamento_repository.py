from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Acompanhamento as AcompanhamentoModel
from app.db.base import ItemPedido as ItemPedidoModel
from app.domain.order_state import StatusPagamento, StatusPedido
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

    def __init__(self, session: AsyncSession):
        self.session = session

    async def criar(self, acompanhamento: Acompanhamento) -> Acompanhamento:
        """Cria um novo acompanhamento no banco de dados"""
        try:
            # Converte modelo de domínio para modelo de banco
            db_acompanhamento = self._to_db_model(acompanhamento)

            self.session.add(db_acompanhamento)
            await self.session.commit()
            await self.session.refresh(db_acompanhamento)

            # Converte de volta para modelo de domínio
            return self._from_db_model(db_acompanhamento)

        except IntegrityError:
            await self.session.rollback()
            raise ValueError(
                f"Já existe acompanhamento para o pedido {acompanhamento.id_pedido}"
            )

    async def buscar_por_id(self, id: int) -> Optional[Acompanhamento]:
        """Busca acompanhamento por ID"""
        db_acompanhamento = await self.session.get(AcompanhamentoModel, id)
        return self._from_db_model(db_acompanhamento) if db_acompanhamento else None

    async def buscar_por_id_pedido(self, id_pedido: int) -> Optional[Acompanhamento]:
        """Busca acompanhamento por ID do pedido"""
        stmt = select(AcompanhamentoModel).where(
            AcompanhamentoModel.id_pedido == id_pedido
        )
        result = await self.session.execute(stmt)
        db_acompanhamento = result.scalar_one_or_none()
        return self._from_db_model(db_acompanhamento) if db_acompanhamento else None

    async def buscar_por_cpf_cliente(self, cpf_cliente: str) -> List[Acompanhamento]:
        """Busca acompanhamentos por CPF do cliente"""
        stmt = (
            select(AcompanhamentoModel)
            .where(AcompanhamentoModel.cpf_cliente == cpf_cliente)
            .order_by(AcompanhamentoModel.atualizado_em.desc())
        )
        result = await self.session.execute(stmt)
        db_acompanhamentos = result.scalars().all()
        return [self._from_db_model(db_acomp) for db_acomp in db_acompanhamentos]

    async def buscar_por_status(
        self, status_list: List[StatusPedido]
    ) -> List[Acompanhamento]:
        """Busca acompanhamentos por lista de status"""
        status_strings = [status.value for status in status_list]
        stmt = (
            select(AcompanhamentoModel)
            .where(AcompanhamentoModel.status.in_(status_strings))
            .order_by(AcompanhamentoModel.atualizado_em.asc())
        )
        result = await self.session.execute(stmt)
        db_acompanhamentos = result.scalars().all()
        return [self._from_db_model(db_acomp) for db_acomp in db_acompanhamentos]

    async def atualizar(self, acompanhamento: Acompanhamento) -> Acompanhamento:
        """Atualiza um acompanhamento existente"""
        # Busca o registro existente
        stmt = select(AcompanhamentoModel).where(
            AcompanhamentoModel.id_pedido == acompanhamento.id_pedido
        )
        result = await self.session.execute(stmt)
        db_acompanhamento = result.scalar_one_or_none()

        if not db_acompanhamento:
            raise ValueError(
                f"Acompanhamento não encontrado para pedido {acompanhamento.id_pedido}"
            )

        # Usamos merge para atualizar (SQLAlchemy cuida da sincronização)
        novo_db_acompanhamento = self._to_db_model(acompanhamento)
        # Preserva o ID existente do banco
        novo_db_acompanhamento.id_acompanhamento = db_acompanhamento.id_acompanhamento

        merged = await self.session.merge(novo_db_acompanhamento)
        await self.session.commit()

        return self._from_db_model(merged)

    async def listar_todos(
        self, skip: int = 0, limit: int = 100
    ) -> List[Acompanhamento]:
        """Lista todos os acompanhamentos com paginação"""
        stmt = (
            select(AcompanhamentoModel)
            .order_by(AcompanhamentoModel.atualizado_em.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        db_acompanhamentos = result.scalars().all()
        return [self._from_db_model(db_acomp) for db_acomp in db_acompanhamentos]

    def _to_db_model(self, acompanhamento: Acompanhamento) -> AcompanhamentoModel:
        """Converte modelo de domínio para modelo de banco"""
        db_acompanhamento = AcompanhamentoModel(
            id_pedido=acompanhamento.id_pedido,
            cpf_cliente=acompanhamento.cpf_cliente,
            status=acompanhamento.status.value,  # Converte enum para string
            status_pagamento=acompanhamento.status_pagamento.value,  # Converte enum para string
            tempo_estimado=acompanhamento.tempo_estimado,
            atualizado_em=acompanhamento.atualizado_em,
        )

        # Cria itens relacionados
        db_itens = []
        for item in acompanhamento.itens:
            db_item = ItemPedidoModel(
                id_produto=item.id_produto,
                id_pedido=acompanhamento.id_pedido,  # FK baseada no id_pedido
                nome_produto=getattr(
                    item, "nome_produto", f"Produto {item.id_produto}"
                ),
                descricao_produto=getattr(item, "descricao_produto", None),
                quantidade=item.quantidade,
                personalizacao=getattr(item, "personalizacao", None),
                categoria=getattr(item, "categoria", None),
            )
            db_itens.append(db_item)

        db_acompanhamento.itens = db_itens
        return db_acompanhamento

    def _from_db_model(self, db_acompanhamento: AcompanhamentoModel) -> Acompanhamento:
        """Converte modelo do banco para modelo de domínio"""
        from app.models.acompanhamento import ItemPedido

        # Converte itens do banco para modelo de domínio
        itens = []
        for db_item in db_acompanhamento.itens:
            item = ItemPedido(
                id_produto=db_item.id_produto,
                quantidade=db_item.quantidade,
            )
            itens.append(item)

        return Acompanhamento(
            id_pedido=getattr(db_acompanhamento, "id_pedido"),
            cpf_cliente=getattr(db_acompanhamento, "cpf_cliente"),
            status=StatusPedido(db_acompanhamento.status),  # Converte string para enum
            status_pagamento=StatusPagamento(
                db_acompanhamento.status_pagamento
            ),  # Converte string para enum
            itens=itens,
            tempo_estimado=getattr(db_acompanhamento, "tempo_estimado"),
            atualizado_em=getattr(db_acompanhamento, "atualizado_em"),
        )
