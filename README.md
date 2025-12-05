# Hidrometro

## Setup Rápido (Windows/PowerShell)
- Pré-requisitos:
	- Python 3.11 (recomendado para compatibilidade com FastAPI/Pydantic v2)
	- Git
	- Docker Desktop (opcional, para banco Postgres local)

- Clonar o repositório:
	- `git clone https://github.com/jadarau/hidrometro.git`
	- `cd hidrometro`

- Back-end (API FastAPI)
	- Criar e ativar o ambiente virtual:
		- ```pwsh
			Set-Location C:\projects\hidrometro\back-end
			py -3.11 -m venv .venv
			.\.venv\Scripts\Activate.ps1
			```
	- Instalar dependências:
		- ```pwsh
			pip install --upgrade pip setuptools wheel
			pip install -r requirements.txt
			```
	- Configurar variáveis de ambiente via arquivo `.env` (não versionado):
		- Crie `back-end/.env` com:
			- ```
				GROQ_API_KEY=<sua_nova_chave_groq>
				GROQ_MODEL=meta-llama/llama-4-maverick-17b-128e-instruct
				DATABASE_URL=postgresql+psycopg://ocruser:ocrpass@localhost:5432/hidrometro
				```
		- Observação: o projeto carrega automaticamente `.env` via `python-dotenv` em `app/__init__.py`.
	- Subir banco Postgres (opcional) com Docker:
		- ```pwsh
			docker compose -f docker-compose.db.yml up -d
			```
	- Rodar a API:
		- ```pwsh
			uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
			```
	- Testar endpoints:
		- Documentação interativa: `http://localhost:8000/docs`
		- Saúde: `http://localhost:8000/health`

- Front-end
	- Caso exista client app em `front-end/`, instale e rode conforme o gerenciador (ex.: `npm i && npm run dev`). Este README foca no back-end.

## Notas de Segurança
- Nunca commitar segredos (API keys, `.env`). O `.gitignore` já ignora `.env` e artefatos locais.
- Se uma chave vazar, revogue e gere outra imediatamente.
- Em produção, use gerenciadores de segredos (Azure Key Vault, etc.) e variáveis de ambiente do serviço.

## Solução de Problemas
- "No module named 'app'":
	- Rode os comandos a partir de `back-end` e com o venv ativo.
	- Alternativa: `Set-Location C:\projects\hidrometro\back-end; $env:PYTHONPATH = "C:\projects\hidrometro\back-end"`.
- "pydantic_core._pydantic_core ausente":
	- Use Python 3.11. Crie o venv com `py -3.11 -m venv .venv` e reinstale dependências.
- Banco local via Docker:
	- `docker compose -f docker-compose.db.yml up -d` antes de iniciar a API.

## Comandos Úteis
- Criar venv (Py 3.11):
	- ```pwsh
		py -3.11 -m venv .venv
		.\.venv\Scripts\Activate.ps1
		```
- Instalar dependências:
	- ```pwsh
		pip install -r requirements.txt
		```
- Rodar API:
	- ```pwsh
		uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
		```
- Subir Postgres:
	- ```pwsh
		docker compose -f docker-compose.db.yml up -d
		```

## Estrutura
- `back-end/app/main.py`: entrada FastAPI
- `back-end/app/config/settings.py`: configurações via `os.getenv` (carregadas do `.env`)
- `back-end/requirements.txt`: dependências
- `back-end/docker-compose.db.yml`: Postgres local
- `back-end/.env`: variáveis locais (não versionado)
