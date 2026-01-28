"""
Estado: Gera relatório final.
"""
import json
from pathlib import Path
from datetime import datetime
from src.core.state import SextantState
from src.states.done import DoneState
from src.utils.config import settings
import pandas as pd


class GenerateReportState(SextantState):
    """Gera relatório final da auditoria"""
    
    async def execute(self, context):
        try:
            self.logger.info("Generating audit report...")
            
            output_dir = context.get("output_dir", settings.OUTPUT_DIR)
            if isinstance(output_dir, str):
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            audit_results_dir = output_dir / "audit_results"
            audit_results_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Gera relatório Markdown
            report_path = audit_results_dir / f"audit_report_{timestamp}.md"
            self._gerar_relatorio_markdown(context, report_path)
            
            # Gera CSV com resultados
            csv_path = audit_results_dir / f"audit_results_{timestamp}.csv"
            self._gerar_csv(context, csv_path)
            
            # Gera JSON com métricas
            json_path = audit_results_dir / f"audit_metrics_{timestamp}.json"
            self._gerar_json(context, json_path)
            
            self.logger.info(f"Reports generated in {audit_results_dir}")
            self.logger.info(f"  - Markdown: {report_path.name}")
            self.logger.info(f"  - CSV: {csv_path.name}")
            self.logger.info(f"  - JSON: {json_path.name}")
            
            context["report_path"] = report_path
            context["csv_path"] = csv_path
            context["json_path"] = json_path
            
            self._log_transition("DoneState", {
                "report_path": str(report_path)
            })
            
            return DoneState()
        
        except Exception as e:
            self._log_error(e)
            raise
    
    def _gerar_relatorio_markdown(self, context: dict, path: Path):
        """Gera relatório em Markdown"""
        resultados = context.get("resultados", [])
        metricas = context.get("metricas")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Relatório de Auditoria - Sextant Banking Edition\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Resumo executivo
            f.write("## Resumo Executivo\n\n")
            if metricas:
                f.write(f"- **Total de Casos**: {metricas.total_casos}\n")
                f.write(f"- **Casos Pass**: {metricas.casos_pass} ({metricas.taxa_acerto:.1%})\n")
                f.write(f"- **Casos Fail**: {metricas.casos_fail}\n")
                f.write(f"- **Casos Partial**: {metricas.casos_partial}\n")
                f.write(f"- **ISR Médio**: {metricas.isr_medio:.3f}\n")
                f.write(f"- **Taxa de Acessibilidade**: {metricas.taxa_acessibilidade:.1%}\n")
                if metricas.flesch_kincaid_medio:
                    f.write(f"- **Flesch-Kincaid Médio**: {metricas.flesch_kincaid_medio:.1f}\n")
                if metricas.disparate_impact:
                    f.write(f"- **Disparate Impact**: {metricas.disparate_impact:.3f}\n")
            f.write("\n")
            
            # Tabela de resultados
            f.write("## Resultados Detalhados\n\n")
            f.write("| ID | Tipo | Decisão IA | Status | Pontos | Acessível? | Passou na Agulha? |\n")
            f.write("|----|------|------------|--------|--------|-------------|-------------------|\n")
            
            for r in resultados:
                decisao = r.resposta_modelo.decisao.value if r.resposta_modelo else "N/A"
                tipo = r.caso_id.split("_")[0] if "_" in r.caso_id else "OUTRO"
                passou_agulha = "✓" if r.status == "PASS" else "✗"
                acessivel = "✓" if r.eh_acessivel else "✗"
                
                f.write(
                    f"| {r.caso_id} | {tipo} | {decisao} | {r.status} | "
                    f"{r.pontos:.2f} | {acessivel} | {passou_agulha} |\n"
                )
            
            f.write("\n")
            
            # Métricas por categoria
            if context.get("metricas_por_categoria"):
                f.write("## Métricas por Categoria\n\n")
                f.write("| Categoria | Total | Pass | Taxa Acerto | ISR Médio | Acessibilidade |\n")
                f.write("|-----------|-------|------|-------------|-----------|----------------|\n")
                
                for m in context["metricas_por_categoria"]:
                    f.write(
                        f"| {m.categoria} | {m.total} | {m.pass_count} | "
                        f"{m.taxa_acerto:.1%} | {m.isr_medio:.3f} | "
                        f"{m.taxa_acessibilidade:.1%} |\n"
                    )
                f.write("\n")
            
            # Vieses detectados
            if metricas and metricas.vieses_detectados:
                f.write("## Vieses Detectados\n\n")
                for vies in metricas.vieses_detectados:
                    f.write(f"- {vies}\n")
                f.write("\n")
    
    def _gerar_csv(self, context: dict, path: Path):
        """Gera CSV com resultados"""
        resultados = context.get("resultados", [])
        
        rows = []
        for r in resultados:
            rows.append({
                "caso_id": r.caso_id,
                "cliente_id": r.cliente_id or "",
                "status": r.status,
                "pontos": r.pontos,
                "eh_acessivel": r.eh_acessivel,
                "decisao": r.resposta_modelo.decisao.value if r.resposta_modelo else "",
                "confianca": r.resposta_modelo.confianca if r.resposta_modelo else 0.0,
                "tem_explicacao": bool(r.resposta_modelo.explicacao_acessivel if r.resposta_modelo else False),
                "vieses": ", ".join(r.vieses_detectados),
                "feedback": r.feedback,
                "discrepancia": r.discrepancia or ""
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, encoding="utf-8")
    
    def _gerar_json(self, context: dict, path: Path):
        """Gera JSON com métricas"""
        metricas = context.get("metricas")
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "metricas": metricas.model_dump() if metricas else None,
            "metricas_por_categoria": [
                m.model_dump() for m in context.get("metricas_por_categoria", [])
            ]
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
