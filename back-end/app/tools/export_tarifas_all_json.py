import json
import sys
from typing import List

from sqlalchemy.orm import Session
from app.infrastructure.db import SessionLocal
from app.infrastructure.orm_models import TarifaAnoDB
from app.models.schemas import TipoImovel, CategoriaLigacao
from app.services.faturas_service import carregar_tarifas_xlsx


def gerar_todas_tarifas(caminho_xlsx: str, ano: int, db: Session) -> dict:
    tarifas_items: List[dict] = []
    for tipo in TipoImovel:
        for categoria in CategoriaLigacao:
            try:
                tid = carregar_tarifas_xlsx(db, caminho_xlsx, ano, tipo, categoria)
            except Exception as e:
                # Loga combinação ignorada para facilitar diagnóstico
                print(f"[aviso] Sem dados ou erro para ano={ano}, tipo={tipo}, categoria={categoria}: {e}", file=sys.stderr)
                continue
            t = db.query(TarifaAnoDB).filter(TarifaAnoDB.id == tid).first()
            if not t:
                print(f"[aviso] Tarifa não encontrada após carga: ano={ano}, tipo={tipo}, categoria={categoria}", file=sys.stderr)
                continue
            item = {
                "ano": t.ano,
                "tipo_imovel": t.tipo,
                "categoria_ligacao": t.categoria_ligacao,
                "faixas": [],
            }
            for f in t.faixas:
                item["faixas"].append(
                    {
                        "faixa": f.faixa,
                        "consumo_min": f.consumo_min,
                        "consumo_max": f.consumo_max,
                        "valor_minimo": (f.valor_minimo / 100.0) if f.valor_minimo is not None else None,
                        "valor_por_m3": (f.valor_por_m3 / 100.0) if f.valor_por_m3 is not None else None,
                    }
                )
            tarifas_items.append(item)
    return {"tarifas": tarifas_items}


def main():
    if len(sys.argv) < 3:
        print(
            "Uso: python -m app.tools.export_tarifas_all_json <caminho_xlsx> <ano>",
            file=sys.stderr,
        )
        sys.exit(1)

    caminho = sys.argv[1]
    ano = int(sys.argv[2])
    db = SessionLocal()
    try:
        payload = gerar_todas_tarifas(caminho, ano, db)
        if not payload.get("tarifas"):
            print("[erro] Nenhuma tarifa exportada. Verifique o caminho do XLSX e o ano informado.", file=sys.stderr)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()