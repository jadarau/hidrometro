from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def seed_pessoas(n=5):
    for i in range(n):
        payload = {
            "tipo_doc": "CPF",
            "documento": f"000000000{i:02d}",
            "nome": f"Pessoa{i}",
            "sobre_nome": "Teste",
            "nascimento": "2000-01-01",
            "sexo": "INDEFINIDO",
            "ativo": True,
            "id_endereco_fatura": None,
        }
        r = client.post("/api/cadastro/pessoas", json=payload)
        assert r.status_code == 200


def seed_imoveis():
    # garante uma pessoa
    rp = client.post(
        "/api/cadastro/pessoas",
        json={
            "tipo_doc": "CPF",
            "documento": "99999999999",
            "nome": "Joao",
            "sobre_nome": "Silva",
            "nascimento": "1990-01-01",
            "sexo": "MASCULINO",
            "ativo": True,
            "id_endereco_fatura": None,
        },
    )
    assert rp.status_code == 200
    pessoa = rp.json()
    pid = pessoa["matricula"]

    imoveis = [
        {
            "id_pessoa": pid,
            "categoria": "LIGAÇÕES MEDIDAS",
            "tipo": "Residencial Social",
            "endereco": "Rua A",
            "numero": "10",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01000-000",
            "esgoto": True,
            "consumo_misto": False,
        },
        {
            "id_pessoa": pid,
            "categoria": "LIGAÇÕES MEDIDAS",
            "tipo": "Residencial Social",
            "endereco": "Rua B",
            "numero": "20",
            "bairro": "Centro",
            "cidade": "Santos",
            "uf": "SP",
            "cep": "11000-000",
            "esgoto": True,
            "consumo_misto": False,
        },
        {
            "id_pessoa": pid,
            "categoria": "LIGAÇÕES NÃO MEDIDAS",
            "tipo": "Residencial Social",
            "endereco": "Rua C",
            "numero": "30",
            "bairro": "Centro",
            "cidade": "Campinas",
            "uf": "SP",
            "cep": "13000-000",
            "esgoto": False,
            "consumo_misto": True,
        },
    ]
    for i in imoveis:
        r = client.post("/api/cadastro/imoveis", json=i)
        assert r.status_code == 200


def test_paginacao_pessoas_headers_e_body():
    seed_pessoas(n=25)
    r = client.get(
        "/api/cadastro/pessoas",
        params={"page": 2, "page_size": 10, "sort_by": "nome", "order": "asc"},
    )
    assert r.status_code == 200
    data = r.json()
    # headers
    assert r.headers.get("X-Total-Count") is not None
    assert r.headers.get("X-Page") == "2"
    assert r.headers.get("X-Page-Size") == "10"
    # body meta
    assert data["meta"]["page"] == 2
    assert data["meta"]["page_size"] == 10
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 10


def test_paginacao_imoveis_headers_e_body():
    seed_imoveis()
    r = client.get(
        "/api/cadastro/imoveis",
        params={"page": 1, "page_size": 2, "sort_by": "cidade", "order": "asc"},
    )
    assert r.status_code == 200
    data = r.json()
    # headers
    assert r.headers.get("X-Total-Count") is not None
    assert r.headers.get("X-Page") == "1"
    assert r.headers.get("X-Page-Size") == "2"
    # body meta
    assert data["meta"]["page"] == 1
    assert data["meta"]["page_size"] == 2
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 2


def test_paginacao_primeira_ultima_e_ordem_portugues():
    # seed suficientes para múltiplas páginas
    seed_pessoas(n=35)

    # última página com page_size=10
    r_last = client.get(
        "/api/cadastro/pessoas",
        params={"page": "última", "page_size": 10, "sort_by": "nome", "order": "decrescente"},
    )
    assert r_last.status_code == 200
    data_last = r_last.json()
    # headers
    assert r_last.headers.get("X-Page") == str(data_last["meta"]["page"])
    # deve conter <= page_size itens na última página
    assert len(data_last["items"]) <= 10

    # primeira página com ordem crescente
    r_first = client.get(
        "/api/cadastro/pessoas",
        params={"page": "primeira", "page_size": 10, "sort_by": "nome", "order": "crescente"},
    )
    assert r_first.status_code == 200
    data_first = r_first.json()
    assert data_first["meta"]["page"] == 1
    assert len(data_first["items"]) <= 10


def test_paginacao_imoveis_primeira_ultima_ordem_portugues():
    # prepara imóveis suficientes
    seed_imoveis()
    # insere mais imóveis para múltiplas páginas
    # cria pessoa extra
    rp = client.post(
        "/api/cadastro/pessoas",
        json={
            "tipo_doc": "CPF",
            "documento": "88888888888",
            "nome": "Ana",
            "sobre_nome": "Lima",
            "nascimento": "1992-02-02",
            "sexo": "FEMININO",
            "ativo": True,
            "id_endereco_fatura": None,
        },
    )
    assert rp.status_code == 200
    pid = rp.json()["matricula"]

    for n, cidade in enumerate(["Guarulhos", "Barueri", "Osasco", "Sorocaba", "Diadema", "Jundiaí"]):
        r = client.post(
            "/api/cadastro/imoveis",
            json={
                "id_pessoa": pid,
                "categoria": "LIGAÇÕES MEDIDAS",
                "tipo": "Residencial Social",
                "endereco": f"Rua {n}",
                "numero": f"{100+n}",
                "bairro": "Centro",
                "cidade": cidade,
                "uf": "SP",
                "cep": f"0{n:02d}00-000",
                "esgoto": True,
                "consumo_misto": False,
            },
        )
        assert r.status_code == 200

    # última página, ordenação decrescente por cidade
    r_last = client.get(
        "/api/cadastro/imoveis",
        params={"page": "última", "page_size": 3, "sort_by": "cidade", "order": "decrescente"},
    )
    assert r_last.status_code == 200
    data_last = r_last.json()
    assert r_last.headers.get("X-Page") == str(data_last["meta"]["page"])
    assert len(data_last["items"]) <= 3

    # primeira página, ordenação crescente
    r_first = client.get(
        "/api/cadastro/imoveis",
        params={"page": "primeira", "page_size": 3, "sort_by": "cidade", "order": "crescente"},
    )
    assert r_first.status_code == 200
    data_first = r_first.json()
    assert data_first["meta"]["page"] == 1
    assert len(data_first["items"]) <= 3


def test_paginacao_clamp_para_ultima_pagina():
    # cria 12 pessoas, page_size=5 => total 3 páginas
    seed_pessoas(n=12)
    r = client.get(
        "/api/cadastro/pessoas",
        params={"page": 9999, "page_size": 5, "sort_by": "nome", "order": "asc"},
    )
    assert r.status_code == 200
    data = r.json()
    # última página esperada: ceil(12/5)=3
    assert data["meta"]["page"] == 3
    assert r.headers.get("X-Page") == "3"
