# OCR Pipeline (Python + EasyOCR)

This project provides a minimal OCR pipeline for images and PDFs using EasyOCR, with optional preprocessing via OpenCV and PDF-to-image conversion via pdf2image.

## Setup (PowerShell)

```powershell
# From the project root (Python 3.11 recomendado)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip wheel
pip install -r requirements.txt

# For PDF support, you need Poppler installed (Windows):
# 1. Download a Poppler build (e.g., from https://github.com/oschwartz10612/poppler-windows/releases)
# 2. Extract and add its `bin` folder to your PATH.
```

## Usage

```powershell
# Basic OCR on an image (CLI tool)
python .\app\tools\ocr.py .\data\sample.png -o .\data\sample.txt

# OCR on a PDF (todas as páginas)
python .\app\tools\ocr.py .\data\sample.pdf -o .\data\sample_pdf.txt

# Salvar saída por página (gera sample_pdf_page1.txt, sample_pdf_page2.txt, ...)
python .\app\tools\ocr.py .\data\sample.pdf -o .\data\sample_pdf.txt --per-page

# Specify language (default: pt for Portuguese)
python .\app\tools\ocr.py .\data\sample.png -l pt

# Include confidence values
python .\app\tools\ocr.py .\data\sample.png -d
```

## API (FastAPI)

### Executar Banco de Dados (PostgreSQL)

1. Instale Docker Desktop.
2. Suba o Postgres com volume persistente no Windows:

```powershell
docker compose -f docker-compose.db.yml up -d
```

O volume persiste em `C:\bancos\hidrometro\db`.

#### Remover container, volumes e imagem do banco

```powershell
# Derrubar o Postgres e remover volumes
docker compose -f docker-compose.db.yml down -v

# Opcional: remover a imagem do Postgres utilizada pelo compose
# (PowerShell: remove todas as imagens 'postgres')
docker images | Where-Object { $_.Repository -eq "postgres" } | ForEach-Object { docker image rm $_.ID }

# Limpeza geral de imagens não utilizadas (opcional)
docker image prune -f
```

### Rodar a API

```powershell
### Rodar a API

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py -3.11 -m uvicorn app.main:app --reload --port 3000
```

Acesse `http://localhost:3000/docs` (Swagger).

#### Script de inicialização simplificada

Use o script `run.ps1` para automatizar venv + dependências + subida do servidor:

```powershell
# Na pasta back-end
Set-Location .\back-end
./run.ps1            # sobe na porta 3000
./run.ps1 -Port 9000 # muda a porta
./run.ps1 -Reinstall # força reinstalação das dependências
```

#### Verificação rápida de saúde
```powershell
# Testar disponibilidade do servidor
Invoke-WebRequest "http://localhost:3000/health" | Select-Object -ExpandProperty Content
```

```powershell
# Preparar ambiente
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Iniciar na porta padrão 3000 (entrypoint)
py -3.11 -m app

# Alterar porta via CLI
py -3.11 -m app --port 9000

# Alternativa clássica: uvicorn com porta explícita
py -3.11 -m uvicorn app.main:app --reload --port 3000
```

Acesse `http://localhost:3000/docs` (Swagger).

### Endpoints de Cadastro

- Pessoas: `/api/cadastro/pessoas`
	- Filtros: `tipo_doc`, `documento`, `nome`, `sobre_nome`, `sexo`, `ativo`, `nascimento`
	- Paginação: `page`, `page_size`
	- Ordenação: `sort_by` (ex.: `nome`), `order` (`asc|desc`)
	- Retorno: `{ items: Pessoa[], meta: { total, page, page_size } }`

- Imóveis: `/api/cadastro/imoveis`
	- Filtros: `cidade`, `categoria`, `ativo`, `cep`
	- Paginação: `page`, `page_size`
	- Ordenação: `sort_by` (ex.: `cidade`), `order` (`asc|desc`)
	- Retorno: `{ items: Imovel[], meta: { total, page, page_size } }`

#### Referência rápida de ordenação (`sort_by`)
- Pessoas: `nome`, `sobre_nome`, `documento`, `nascimento`, `sexo`, `ativo`
- Imóveis: `cidade`, `cep`, `categoria`, `tipo`, `numero`, `matricula`

Notas:
- `order` aceita `asc|desc` e sinônimos em português: `crescente|decrescente`.
- Se um `sort_by` inválido for fornecido, a API ignora e usa o padrão do endpoint.

#### Paginação avançada
- `page` aceita:
	- Número da página (`1`, `2`, ...)
	- `primeira` ou `first`
	- `última`/`ultima` ou `last`
- Se a página solicitada exceder o total, a API ajusta para a última página disponível.

#### Ordenação em português
- `order` aceita:
	- `asc` ou `crescente`
	- `desc` ou `decrescente`

### Exemplos rápidos

```powershell
# Pessoas: listar página 1, 20 itens, ordenado por nome asc
Invoke-WebRequest "http://localhost:3000/api/cadastro/pessoas?ativo=true&sort_by=nome&order=asc&page=1&page_size=20"

# Imóveis: listar por cidade parcial, sort por cidade desc
Invoke-WebRequest "http://localhost:3000/api/cadastro/imoveis?cidade=São&page=1&page_size=20&sort_by=cidade&order=desc"

# Pessoas: última página com ordenação decrescente
Invoke-WebRequest "http://localhost:3000/api/cadastro/pessoas?sort_by=nome&order=decrescente&page=última&page_size=10"

# Imóveis: primeira página com ordenação crescente
Invoke-WebRequest "http://localhost:3000/api/cadastro/imoveis?sort_by=cidade&order=crescente&page=primeira&page_size=10"

#### Exemplo de resposta com cabeçalhos de paginação

Cabeçalhos retornados:
- `X-Total-Count`: total de registros
- `X-Page`: página atual após resolução/clamp
- `X-Page-Size`: tamanho da página

Exemplo de corpo:

```json
{
	"items": [
		{ "matricula": 1001, "cidade": "São Paulo", "cep": "01000-000", "numero": "123", "categoria": "RESIDENCIAL", "tipo": "CASA" }
	],
	"meta": { "total": 57, "page": 3, "page_size": 20 }
}
```
```

### Exemplos por endpoint

#### Saúde
```powershell
Invoke-WebRequest "http://localhost:3000/health" | Select-Object -ExpandProperty Content
```

#### Hidrometro: leitura
```powershell
curl -X POST "http://localhost:3000/api/hydrometer/read" `
	-H "Accept: application/json" `
	-F "lang=pt" `
	-F "detail=false" `
	-F "files=@data/sample.png;type=image/png"
```

#### Pessoas
- Criar
```powershell
Invoke-RestMethod -Method POST -ContentType application/json `
	-Uri "http://localhost:3000/api/cadastro/pessoas" `
	-Body '{
		"tipo_doc": "CPF",
		"documento": "12345678900",
		"nome": "Joao",
		"sobre_nome": "Silva",
		"nascimento": "1990-01-01",
		"sexo": "MASCULINO",
		"ativo": true,
		"id_endereco_fatura": null
	}'
```
- Listar com filtros, paginação e ordenação
```powershell
Invoke-WebRequest "http://localhost:3000/api/cadastro/pessoas?ativo=true&sort_by=nome&order=asc&page=1&page_size=20"
```
- Obter por matrícula
```powershell
Invoke-WebRequest "http://localhost:3000/api/cadastro/pessoas/1"
```
- Atualizar
```powershell
Invoke-RestMethod -Method PUT -ContentType application/json `
	-Uri "http://localhost:3000/api/cadastro/pessoas/1" `
	-Body '{
		"tipo_doc": "CPF",
		"documento": "12345678900",
		"nome": "Joao",
		"sobre_nome": "Silva",
		"nascimento": "1990-01-01",
		"sexo": "MASCULINO",
		"ativo": true,
		"id_endereco_fatura": null
	}'
```
- Remover
```powershell
Invoke-RestMethod -Method DELETE -Uri "http://localhost:3000/api/cadastro/pessoas/1"
```

#### Imóveis
- Criar
```powershell
Invoke-RestMethod -Method POST -ContentType application/json `
	-Uri "http://localhost:3000/api/cadastro/imoveis" `
	-Body '{
		"id_pessoa": 1,
		"categoria": "LIGAÇÕES MEDIDAS",
		"tipo": "Residencial Social",
		"endereco": "Rua A",
		"numero": "123",
		"bairro": "Centro",
		"cidade": "São Paulo",
		"uf": "SP",
		"cep": "01000-000",
		"esgoto": true,
		"consumo_misto": false
	}'
```
- Listar com filtros, paginação e ordenação
```powershell
Invoke-WebRequest "http://localhost:3000/api/cadastro/imoveis?cidade=São&page=1&page_size=20&sort_by=cidade&order=desc"
```
- Obter por matrícula
```powershell
Invoke-WebRequest "http://localhost:3000/api/cadastro/imoveis/1"
```
- Atualizar
```powershell
Invoke-RestMethod -Method PUT -ContentType application/json `
	-Uri "http://localhost:3000/api/cadastro/imoveis/1" `
	-Body '{
		"id_pessoa": 1,
		"categoria": "LIGAÇÕES MEDIDAS",
		"tipo": "Residencial Social",
		"endereco": "Rua A",
		"numero": "123",
		"bairro": "Centro",
		"cidade": "São Paulo",
		"uf": "SP",
		"cep": "01000-000",
		"esgoto": true,
		"consumo_misto": false
	}'
```
- Remover
```powershell
Invoke-RestMethod -Method DELETE -Uri "http://localhost:3000/api/cadastro/imoveis/1"
```

### Postman

Importe `docs/postman/cadastro.postman_collection.json` para ter todas as requisições de Pessoas e Imóveis com exemplos de filtros, paginação e ordenação.

### Hidrometro + GROQ

Opção recomendada: defina `GROQ_API_KEY` via ambiente.

```powershell
$env:GROQ_API_KEY = "SEU_TOKEN_AQUI"
py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# Leitura de hidrômetro (retorna { results: [ { filename, valor_da_leitura } ] })
curl -X POST "http://localhost:8000/api/hydrometer/read" ^
	-F "lang=pt" -F "detail=false" ^
	-F "files=@data/sample.png"
```

### Formas de inicialização

```powershell
# 1) uvicorn via py launcher (recomendado)
py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# 2) uvicorn do venv
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 3000 --reload

# 3) via Python absoluto (se preferir apontar caminho do 3.11)
"C:\Users\jadson.araujo\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# Dica: ative o venv antes para garantir pacotes corretos
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
```

Opção fixa (não recomendada): colocar a chave diretamente em `app/services/settings.py` no campo `groq_api_key`.
Isso é útil apenas para ambientes controlados; evite em produção.

#### Validações
- Tipos aceitos: `png`, `jpg`, `jpeg`, `pdf`.
- Tamanho máximo por arquivo: `MAX_FILE_SIZE_MB` (padrão 10 MB) — configurável via env.
- Máximo de páginas por PDF: `MAX_PDF_PAGES` (padrão 5) — excedentes são ignoradas.

#### Troubleshooting (Groq SDK / httpx)
- Erro `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'` indica incompatibilidade entre versões do `groq` e `httpx`.
- Solução aplicada: pin `httpx==0.27.2` no `requirements.txt`.
- Caso persista, reinstale dependências:
```powershell
pip install --force-reinstall -r .\requirements.txt
```
- Fallback automático: se o SDK falhar, a aplicação usa requisição direta HTTP (`requests`) para a API Groq.

#### Curl completo (hidrômetro)

```powershell
# Certifique-se de que a API está rodando e a GROQ_API_KEY configurada
$env:GROQ_API_KEY = "SEU_TOKEN_AQUI"
py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# Requisição completa com múltiplos anexos (imagem + PDF)
curl -X POST "http://localhost:8000/api/hydrometer/read" `
	-H "Accept: application/json" `
	-F "lang=pt" `
	-F "detail=false" `
	-F "files=@data/hidrometro1.jpg;type=image/jpeg" `
	-F "files=@data/hidrometro2.png;type=image/png" `
	-F "files=@data/hidrometro.pdf;type=application/pdf"

# Resposta esperada (exemplo)
# {
#   "results": [
#     { "filename": "hidrometro1.jpg", "valor_da_leitura": "123456" },
#     { "filename": "hidrometro2.png", "valor_da_leitura": "123457" },
#     { "filename": "hidrometro.pdf", "valor_da_leitura": "123458" }
#   ]
# }
```

## Notes

- EasyOCR supports multiple languages; install additional language models automatically when first used.
- OpenCV preprocessing can improve accuracy; disable by uninstalling OpenCV or modify `_preprocess` in `src/ocr.py`.
- For PDFs, ensure Poppler is installed and on PATH.
- O flag `--per-page` salva um arquivo `.txt` por página quando o input é PDF.
