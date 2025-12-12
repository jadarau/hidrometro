from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TipoDocumento(str, Enum):
    CPF = "CPF"
    CNH = "CNH"
    CTPS = "CTPS"
    PASSAPORTE = "PASSAPORTE"


class Sexo(str, Enum):
    MASCULINO = "MASCULINO"
    FEMININO = "FEMININO"
    TRANS_HOMEM = "TRANS_HOMEM"
    TRANS_MULHER = "TRANS_MULHER"
    INDEFINIDO = "INDEFINIDO"


class CategoriaLigacao(str, Enum):
    LIGACOES_MEDIDAS = "LIGAÇÕES MEDIDAS"
    LIGACOES_NAO_MEDIDAS = "LIGAÇÕES NÃO MEDIDAS"
    DERIVACOES_RURAIS = "DERIVAÇÕES RURAIS"
    ESGOTAMENTO_SANITARIO = "ESGOTAMENTO SANITÁRIO"



class TipoImovel(str, Enum):
    RESIDENCIAL_SOCIAL = "Residencial Social"
    RESIDENCIAL_INTERMEDIARIA = "Residêncial Intermediária"
    RESIDENCIAL_NORMAL_VERANEIO = "Residencial / Normal / Veraneio"
    FILANTROPICA = "Filantrópica"
    COMERCIAL = "Comercial"
    SERVICOS = "Serviços"
    ATIVIDADES_REDUZIDAS = "Comércios e outras atividades reduzidas"
    DERIVACOES_COMERCIAIS_AGUA_BRUTA = "Derivações Comerciais de Água Bruta"
    CONSTRUCAO_E_INDUSTRIAL = "Construção e Industrial"
    PUBLICA = "Pública"
    SERVICOS_ATIVIDADES_NORMAL = "Serviços, comércios e outras atividades normal"
    SERVICOS_ATIVIDADES_REDUZIDAS = "Serviços, comércios e outras atividades reduzidas"
    CONSTRUCAO_OU_INDUSTRIAL_ = "Construção / Industrial"
    AGUA_TRATADA = "Água Tratada"
    AGUA_BRUTA = "Água Bruta"
    SISTEMAS_CONV_CAPITAL = "Sistemas Convencionais (Capital)"
    SISTEMAS_CONV_INTERIOR = "Sistemas Convencionais (Interior)"


class PessoaCreate(BaseModel):
    tipo_doc: TipoDocumento
    documento: str
    nome: str
    sobre_nome: str
    nascimento: str
    sexo: Sexo
    ativo: bool = True
    id_endereco_fatura: Optional[int] = None


class Pessoa(BaseModel):
    matricula: int
    tipo_doc: TipoDocumento
    documento: str
    nome: str
    sobre_nome: str
    nascimento: str
    sexo: Sexo
    ativo: bool
    id_endereco_fatura: Optional[int] = None


class ImovelCreate(BaseModel):
    id_pessoa: int
    categoria: CategoriaLigacao
    tipo: TipoImovel
    endereco: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    esgoto: bool
    consumo_misto: bool


class Imovel(BaseModel):
    matricula: int
    id_pessoa: int
    categoria: CategoriaLigacao
    tipo: TipoImovel
    endereco: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    esgoto: bool
    consumo_misto: bool


# Existing hydrometer schemas kept below

class HydrometerResult(BaseModel):
    filename: str
    valor_da_leitura: str

class HydrometerResponse(BaseModel):
    results: List[HydrometerResult]


# Paginação com metadados
class PageMeta(BaseModel):
    total: int
    page: int
    page_size: int


class PessoasPage(BaseModel):
    items: List[Pessoa]
    meta: PageMeta


class ImoveisPage(BaseModel):
    items: List[Imovel]
    meta: PageMeta

# Tarifa schemas
class TarifaFaixa(BaseModel):
    faixa: int
    consumo_min: int
    consumo_max: int | None
    valor_minimo: float | None = None
    valor_por_m3: float | None = None

class TarifaAnoCreate(BaseModel):
    ano: int
    tipo_imovel: TipoImovel
    categoria_ligacao: CategoriaLigacao
    faixas: List[TarifaFaixa]

class TarifaAno(BaseModel):
    id: int
    ano: int
    tipo_imovel: TipoImovel
    categoria_ligacao: CategoriaLigacao
    faixas: List[TarifaFaixa]

class FaturaCalculoRequest(BaseModel):
    matricula_imovel: int
    ano: int
    consumo_m3: int

class FaturaCalculoResponse(BaseModel):
    ano: int
    matricula_imovel: int
    consumo_m3: int
    valor_agua: float
    valor_esgoto: float
    total: float
    detalhamento: List[dict]
