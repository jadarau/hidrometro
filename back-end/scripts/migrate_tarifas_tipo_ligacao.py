import os
import sys
from sqlalchemy import text

# Ensure project root is on sys.path so 'app' can be imported when running the script directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.infrastructure.db import engine

sql = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_ligacao_enum') THEN
        CREATE TYPE tipo_ligacao_enum AS ENUM ('LIGAÇÕES MEDIDAS', 'LIGAÇÕES NÃO MEDIDAS', 'DERIVAÇÕES RURAIS', 'ESGOTAMENTO SANITÁRIO');
    END IF;
END$$;

ALTER TABLE tarifas_ano ADD COLUMN IF NOT EXISTS tipo_ligacao tipo_ligacao_enum;

UPDATE tarifas_ano SET tipo_ligacao = 'LIGAÇÕES MEDIDAS' WHERE tipo_ligacao IS NULL;

ALTER TABLE tarifas_ano DROP CONSTRAINT IF EXISTS uq_tarifa_ano_tipo;
ALTER TABLE tarifas_ano ADD CONSTRAINT uq_tarifa_ano_tipo_ligacao UNIQUE (ano, tipo, tipo_ligacao);
"""

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Migração aplicada: coluna tipo_ligacao adicionada e constraint atualizada.")
