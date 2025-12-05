from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.db import Base
from app.models.schemas import TipoDocumento, Sexo, CategoriaLigacao, TipoImovel


class PessoaDB(Base):
    __tablename__ = "pessoas"
    __table_args__ = (
        UniqueConstraint("documento", name="uq_pessoas_documento"),
    )
    matricula = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo_doc = Column(SAEnum(TipoDocumento), nullable=False)
    documento = Column(String, nullable=False, index=True)
    nome = Column(String, nullable=False, index=True)
    sobre_nome = Column(String, nullable=False, index=True)
    nascimento = Column(String, nullable=False, index=True)
    sexo = Column(SAEnum(Sexo), nullable=False, index=True)
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    id_endereco_fatura = Column(Integer, nullable=True)

    imoveis = relationship("ImovelDB", back_populates="pessoa", cascade="all, delete-orphan")


class ImovelDB(Base):
    __tablename__ = "imoveis"
    matricula = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pessoa = Column(Integer, ForeignKey("pessoas.matricula", ondelete="CASCADE"), nullable=False, index=True)
    categoria = Column(SAEnum(CategoriaLigacao), nullable=False, index=True)
    tipo = Column(SAEnum(TipoImovel), nullable=False, index=True)
    endereco = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    bairro = Column(String, nullable=False)
    cidade = Column(String, nullable=False, index=True)
    uf = Column(String, nullable=False)
    cep = Column(String, nullable=False, index=True)
    esgoto = Column(Boolean, nullable=False)
    consumo_misto = Column(Boolean, nullable=False)

    pessoa = relationship("PessoaDB", back_populates="imoveis")