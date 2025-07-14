from datetime import datetime, timezone

from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Acompanhamento(Base):
    __tablename__ = "acompanhamento"

    id_acompanhamento = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, unique=True, nullable=False)
    cpf_cliente = Column(String(11), nullable=False)
    status = Column(String(50), nullable=False)
    status_pagamento = Column(String(50), nullable=False)
    valor_pago = Column(DECIMAL(10, 2), nullable=True)
    tempo_estimado = Column(String(8), nullable=True)
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    itens = relationship(
        "ItemPedido", back_populates="acompanhamento", cascade="all, delete-orphan"
    )


class ItemPedido(Base):
    __tablename__ = "item_pedido"

    id_produto = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey("acompanhamento.id_pedido"), nullable=False)
    nome_produto = Column(String(100), nullable=False)
    descricao_produto = Column(String(255), nullable=True)
    quantidade = Column(Integer, nullable=False)
    personalizacao = Column(String(255), nullable=True)
    categoria = Column(String(50), nullable=True)

    acompanhamento = relationship("Acompanhamento", back_populates="itens")
