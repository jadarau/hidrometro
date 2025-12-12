import json
import sys
from typing import List

from app.services.faturas_service import carregar_tarifas_xlsx
from app.infrastructure.db import SessionLocal


def main():
    if len(sys.argv) < 5:
        print(
            "Uso: python -m app.tools.export_tarifas_json <caminho_xlsx> <ano> <tipo_imovel> <categoria_ligacao>",
            file=sys.stderr,
        )
        sys.exit(1)

    caminho = sys.argv[1]
    ano = int(sys.argv[2])
    tipo_imovel = sys.argv[3]
    categoria_ligacao = sys.argv[4]

    # Carrega faixas da planilha para a combinação fornecida
    db = SessionLocal()
    try:
        tarifa_id = carregar_tarifas_xlsx(db, caminho, ano, tipo_imovel, categoria_ligacao)
        # Agora consulta a tarifa criada para montar o JSON completo
        from app.infrastructure.orm_models import TarifaAnoDB
        tarifa = db.query(TarifaAnoDB).filter(TarifaAnoDB.id == tarifa_id).first()
        if not tarifa:
            print("Falha ao carregar tarifas do Excel.", file=sys.stderr)
            sys.exit(2)

        item = {
            "ano": tarifa.ano,
            "tipo_imovel": tarifa.tipo,
            "categoria_ligacao": tarifa.categoria_ligacao,
            "faixas": [],
        }
        for f in tarifa.faixas:
            item["faixas"].append(
                {
                    "faixa": f.faixa,
                    "consumo_min": f.consumo_min,
                    "consumo_max": f.consumo_max,
                    "valor_minimo": (f.valor_minimo / 100.0) if f.valor_minimo is not None else None,
                    "valor_por_m3": (f.valor_por_m3 / 100.0) if f.valor_por_m3 is not None else None,
                }
            )

        payload = {"tarifas": [item]}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()