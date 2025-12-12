from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.agents.reading_agent import HydrometerReadingAgent
from app.services.faturas_service import calcular_fatura
from app.infrastructure.db import SessionLocal


def _extract_matricula(filename: str) -> int:
    base = filename.split('/')[-1].split('\\')[-1]
    prefix = base.split('_')[0]
    return int(prefix)


class InvoiceAgent:
    def __init__(self, lang: str = "pt", detail: bool = False):
        self.reader = HydrometerReadingAgent(lang=lang, detail=detail)

    def build_graph(self):
        # Cria grafo de estado para orquestrar leitura -> fatura
        graph = StateGraph(dict)

        def node_read(state: Dict[str, Any]) -> Dict[str, Any]:
            # Nó de leitura: usa HydrometerReadingAgent para obter valor
            # Espera: filename, image (PIL) e opcional valor_da_leitura
            filename = state["filename"]
            value = state.get("valor_da_leitura")
            if value is None:
                img = state["image"]
                value = self.reader.read_from_image(img)
            state["valor_da_leitura"] = str(value)
            return state

        def node_invoice(state: Dict[str, Any]) -> Dict[str, Any]:
            # Nó de fatura: extrai matrícula do nome do arquivo e calcula fatura
            ano = int(state["ano"])  # required
            filename = state["filename"]
            matricula = _extract_matricula(filename)
            leitura_valor = int(str(state["valor_da_leitura"]))
            db = SessionLocal()
            try:
                req = type("Obj", (), {"matricula_imovel": matricula, "ano": ano, "consumo_m3": leitura_valor})
                resp = calcular_fatura(db, req)
                state["invoice"] = {
                    "matricula_imovel": resp.matricula_imovel,
                    "ano": resp.ano,
                    "consumo_m3": resp.consumo_m3,
                    "valor_agua": resp.valor_agua,
                    "valor_esgoto": resp.valor_esgoto,
                    "total": resp.total,
                    "detalhamento": resp.detalhamento,
                }
            finally:
                db.close()
            return state

        # Define nós e fluxo: read -> invoice -> END
        graph.add_node("read", node_read)
        graph.add_node("invoice", node_invoice)
        graph.add_edge("read", "invoice")
        graph.add_edge("invoice", END)
        graph.set_entry_point("read")
        return graph.compile()

    def run(self, filename: str, image, ano: int, valor_da_leitura: int | None = None) -> Dict[str, Any]:
        app = self.build_graph()
        initial = {"filename": filename, "image": image, "ano": ano}
        if valor_da_leitura is not None:
            initial["valor_da_leitura"] = valor_da_leitura
        final = app.invoke(initial)
        return {
            "filename": filename,
            "valor_da_leitura": str(final.get("valor_da_leitura")),
            "invoice": final.get("invoice"),
        }