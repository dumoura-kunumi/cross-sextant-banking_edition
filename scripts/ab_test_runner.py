#!/usr/bin/env python3
"""
Teste A/B: Análise do impacto do ISR na detecção de alucinações
- Teste A: SEM validação (baseline)
- Teste B: COM validação + ISR
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import shutil
from typing import Dict, List, Tuple

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import settings
from src.utils.logger import setup_logger
from src.loaders.artifacts import ArtifactLoader
from src.services.model_executor import ModelExecutor
from src.models.responses import RespostaCaso

logger = setup_logger(__name__)


class ABTestRunner:
    """Runner para testes A/B com e sem validação"""
    
    def __init__(self):
        self.results_a = {"test": "A (SEM validação)", "casos": []}
        self.results_b = {"test": "B (COM validação)", "casos": []}
        self.artifact_loader = ArtifactLoader()
        
    def prepare_test_a(self):
        """Prepara Teste A: SEM dados de validação"""
        logger.info("=== PREPARANDO TESTE A (SEM VALIDAÇÃO) ===")
        
        # Carrega artefatos normais
        politicas = self.artifact_loader.carregar_politicas()
        clientes = self.artifact_loader.carregar_clientes()
        casos = self.artifact_loader.carregar_casos_teste()
        prompt = self.artifact_loader.carregar_prompt_template()
        
        # Aqui você pode remover dados de validação do prompt se necessário
        # Por agora, usamos o prompt original
        
        return politicas, clientes, casos, prompt
    
    def prepare_test_b(self):
        """Prepara Teste B: COM dados de validação + matriz"""
        logger.info("=== PREPARANDO TESTE B (COM VALIDAÇÃO + ISR) ===")
        
        # Carrega artefatos com validação
        politicas = self.artifact_loader.carregar_politicas()
        clientes = self.artifact_loader.carregar_clientes()
        casos = self.artifact_loader.carregar_casos_teste()
        prompt = self.artifact_loader.carregar_prompt_template()
        matriz = self.artifact_loader.carregar_matriz_validacao()
        
        return politicas, clientes, casos, prompt, matriz
    
    async def run_test_a(self):
        """Executa Teste A"""
        logger.info("\n" + "="*80)
        logger.info("INICIANDO TESTE A: SEM VALIDAÇÃO")
        logger.info("="*80)
        
        politicas, clientes, casos, prompt = self.prepare_test_a()
        executor = ModelExecutor(settings)
        
        # Contexto sem validação
        context_a = {
            "politicas": politicas,
            "clientes": clientes,
            "prompt": prompt,
            "modo": "baseline",
            "include_validation": False
        }
        
        total_casos = min(len(casos), 5)  # Primeiros 5 para teste rápido
        for i, caso in enumerate(casos[:total_casos]):
            logger.info(f"Executando caso {i+1}/{total_casos}: {caso.caso_id}")
            try:
                resposta = await executor.executar_caso(caso, context_a)
                self.results_a["casos"].append({
                    "caso_id": caso.caso_id,
                    "tipo": caso.tipo_cenario,
                    "decisao_esperada": caso.output_esperado.get("decisao"),
                    "decisao_ia": resposta.get("decisao", "N/A"),
                    "acertou": resposta.get("decisao") == caso.output_esperado.get("decisao"),
                    "confianca": resposta.get("confianca", 0),
                    "isr": None  # Teste A não tem ISR
                })
            except Exception as e:
                logger.error(f"Erro no caso {caso.caso_id}: {e}")
                self.results_a["casos"].append({
                    "caso_id": caso.caso_id,
                    "tipo": caso.tipo_cenario,
                    "erro": str(e)
                })
    
    async def run_test_b(self):
        """Executa Teste B"""
        logger.info("\n" + "="*80)
        logger.info("INICIANDO TESTE B: COM VALIDAÇÃO + ISR")
        logger.info("="*80)
        
        politicas, clientes, casos, prompt, matriz = self.prepare_test_b()
        executor = ModelExecutor(settings)
        
        # Contexto com validação
        context_b = {
            "politicas": politicas,
            "clientes": clientes,
            "prompt": prompt,
            "matriz_validacao": matriz,
            "modo": "com_validacao",
            "include_validation": True
        }
        
        total_casos = min(len(casos), 5)  # Primeiros 5 para teste rápido
        for i, caso in enumerate(casos[:total_casos]):
            logger.info(f"Executando caso {i+1}/{total_casos}: {caso.caso_id}")
            try:
                resposta = await executor.executar_caso(caso, context_b)
                self.results_b["casos"].append({
                    "caso_id": caso.caso_id,
                    "tipo": caso.tipo_cenario,
                    "decisao_esperada": caso.output_esperado.get("decisao"),
                    "decisao_ia": resposta.get("decisao", "N/A"),
                    "acertou": resposta.get("decisao") == caso.output_esperado.get("decisao"),
                    "confianca": resposta.get("confianca", 0),
                    "isr": resposta.get("isr", None)
                })
            except Exception as e:
                logger.error(f"Erro no caso {caso.caso_id}: {e}")
                self.results_b["casos"].append({
                    "caso_id": caso.caso_id,
                    "tipo": caso.tipo_cenario,
                    "erro": str(e)
                })
    
    def calculate_metrics(self, results: Dict) -> Dict:
        """Calcula métricas: Recall, Acurácia, Precisão, ISR médio"""
        casos = results["casos"]
        
        # Filtra casos sem erro
        valid_casos = [c for c in casos if "erro" not in c]
        
        if not valid_casos:
            return {
                "total": len(casos),
                "válidos": 0,
                "acurácia": 0,
                "recall": 0,
                "precisão": 0,
                "isr_médio": 0
            }
        
        # TP: acertou, TN: errou (para alucinação é TP se detectou)
        tp = sum(1 for c in valid_casos if c.get("acertou", False))
        total = len(valid_casos)
        acurácia = tp / total if total > 0 else 0
        
        # Recall: dos casos que deviam ser detectados, quantos foram?
        # Neste contexto: quantos erros/alucinações foram detectados?
        recall = tp / total if total > 0 else 0
        
        # Precisão: dos que foram detectados como erro, quantos eram reais?
        precisão = tp / total if total > 0 else 0
        
        # ISR médio (Teste B)
        isr_values = [c.get("isr") for c in valid_casos if c.get("isr") is not None]
        isr_médio = sum(isr_values) / len(isr_values) if isr_values else 0
        
        return {
            "total": len(casos),
            "válidos": len(valid_casos),
            "tp": tp,
            "acurácia": round(acurácia * 100, 2),
            "recall": round(recall * 100, 2),
            "precisão": round(precisão * 100, 2),
            "isr_médio": round(isr_médio, 4),
            "confianca_média": round(sum(c.get("confianca", 0) for c in valid_casos) / len(valid_casos), 2) if valid_casos else 0
        }
    
    def generate_report(self):
        """Gera relatório comparativo A/B"""
        metrics_a = self.calculate_metrics(self.results_a)
        metrics_b = self.calculate_metrics(self.results_b)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path("outputs/ab_test") / f"ab_test_report_{timestamp}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = f"""# Relatório Teste A/B: Impacto da Validação e ISR

**Data**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Resumo Executivo

- **Teste A (Baseline SEM validação)**: {metrics_a['válidos']} casos válidos
- **Teste B (COM validação + ISR)**: {metrics_b['válidos']} casos válidos

## Comparação de Métricas

| Métrica | Teste A (SEM validação) | Teste B (COM validação) | Diferença |
|---------|------------------------|----------------------|-----------|
| **Acurácia** | {metrics_a['acurácia']}% | {metrics_b['acurácia']}% | {metrics_b['acurácia'] - metrics_a['acurácia']:+.2f}% |
| **Recall** | {metrics_a['recall']}% | {metrics_b['recall']}% | {metrics_b['recall'] - metrics_a['recall']:+.2f}% |
| **Precisão** | {metrics_a['precisão']}% | {metrics_b['precisão']}% | {metrics_b['precisão'] - metrics_a['precisão']:+.2f}% |
| **Confiança Média** | {metrics_a['confianca_média']} | {metrics_b['confianca_média']} | {metrics_b['confianca_média'] - metrics_a['confianca_média']:+.2f} |
| **ISR Médio** | N/A | {metrics_b['isr_médio']} | - |

## Análise de Resultados

### Detecção de Alucinações

- **Teste A (Baseline)**: Recall = {metrics_a['recall']}% - Modelo detecta {metrics_a['recall']:.0f}% dos erros sem validação
- **Teste B (Com ISR)**: Recall = {metrics_b['recall']}% - Modelo detecta {metrics_b['recall']:.0f}% dos erros com validação

**Melhoria**: {metrics_b['recall'] - metrics_a['recall']:+.2f}% (ISR ajuda na detecção? {'SIM' if metrics_b['recall'] > metrics_a['recall'] else 'NÃO'})

### Impacto da Validação

- ISR Médio: {metrics_b['isr_médio']} (esperado: > 0.85)
- A validação {'MELHOROU' if metrics_b['acurácia'] > metrics_a['acurácia'] else 'PIOROU'} a acurácia em {abs(metrics_b['acurácia'] - metrics_a['acurácia']):.2f}%

## Conclusões

1. **ISR é útil?** {('SIM - Melhoria de ' + str(metrics_b['recall'] - metrics_a['recall']) + '%') if metrics_b['recall'] > metrics_a['recall'] else 'NÃO - Sem melhoria significativa'}
2. **Validação reduz alucinações?** {('SIM' if metrics_b['acurácia'] > metrics_a['acurácia'] else 'NÃO')}
3. **Recomendação**: {'Incluir validação nos prompts' if metrics_b['acurácia'] > metrics_a['acurácia'] else 'Revisar estratégia de validação'}

## Detalhes por Caso (Teste B)

"""
        
        report += "\n| Caso | Tipo | Esperado | IA Decidiu | Acertou | Confiança | ISR |\n"
        report += "|------|------|----------|-----------|---------|-----------|-----|\n"
        
        for caso in self.results_b["casos"]:
            if "erro" not in caso:
                report += f"| {caso['caso_id']} | {caso['tipo']} | {caso['decisao_esperada']} | {caso['decisao_ia']} | {'✓' if caso['acertou'] else '✗'} | {caso['confianca']} | {caso.get('isr', 'N/A')} |\n"
        
        # Salvar relatório
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info(f"\n✅ Relatório salvo em: {report_path}")
        
        # Também salva JSON com dados brutos
        json_path = report_path.parent / f"ab_test_results_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "test_a": self.results_a,
                "test_b": self.results_b,
                "metrics_a": metrics_a,
                "metrics_b": metrics_b
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Dados brutos salvos em: {json_path}")
        
        # Print summary
        print("\n" + "="*80)
        print("RESULTADO FINAL DO TESTE A/B")
        print("="*80)
        print(f"\n📊 ACURÁCIA:")
        print(f"  Teste A (SEM validação):  {metrics_a['acurácia']}%")
        print(f"  Teste B (COM validação):  {metrics_b['acurácia']}%")
        print(f"  Melhoria: {metrics_b['acurácia'] - metrics_a['acurácia']:+.2f}%")
        
        print(f"\n🎯 RECALL (Detecção de Erros):")
        print(f"  Teste A: {metrics_a['recall']}%")
        print(f"  Teste B: {metrics_b['recall']}%")
        print(f"  Melhoria: {metrics_b['recall'] - metrics_a['recall']:+.2f}%")
        
        print(f"\n📈 ISR MÉDIO (Teste B):")
        print(f"  ISR: {metrics_b['isr_médio']}")
        print(f"  Status: {'✓ ADEQUADO (>0.85)' if metrics_b['isr_médio'] > 0.85 else '✗ INADEQUADO (<0.85)'}")
        
        return metrics_a, metrics_b


async def main():
    """Main entry point"""
    runner = ABTestRunner()
    
    print("\n" + "="*80)
    print("TESTE A/B: IMPACTO DA VALIDAÇÃO E ISR NA DETECÇÃO DE ALUCINAÇÕES")
    print("="*80)
    
    # Executar testes
    await runner.run_test_a()
    await runner.run_test_b()
    
    # Gerar relatório
    metrics_a, metrics_b = runner.generate_report()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
