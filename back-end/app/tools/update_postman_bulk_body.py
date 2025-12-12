import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print(
            "Uso: python -m app.tools.update_postman_bulk_body <caminho_collection_json> <caminho_bulk_json>",
            file=sys.stderr,
        )
        sys.exit(1)

    collection_path = Path(sys.argv[1])
    bulk_json_path = Path(sys.argv[2])

    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    bulk_payload = bulk_json_path.read_text(encoding="utf-8")

    # Procura item pelo nome
    for item in collection.get("item", []):
        if item.get("name") == "Criar Tarifas em Lote (JSON)":
            req = item.get("request", {})
            body = req.setdefault("body", {"mode": "raw"})
            body["mode"] = "raw"
            body["raw"] = bulk_payload
            break
    else:
        print("Item 'Criar Tarifas em Lote (JSON)' não encontrado na collection.", file=sys.stderr)
        sys.exit(2)

    collection_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Collection atualizada: {collection_path}")


if __name__ == "__main__":
    main()