#!/usr/bin/env python3
"""
Script para executar Teste A/B completo:
- Teste A: SEM validação/ISR (baseline)
- Teste B: COM validação/ISR
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import subprocess

def run_ab_test():
    """Executa teste A/B com duas rodadas do Sextant"""
    
    project_root = Path(__file__).parent
    outputs_dir = project_root / "outputs"
    ab_test_dir = outputs_dir / "ab_test"
    ab_test_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "="*80)
    print("TESTE A/B: IMPACTO DA VALIDAÇÃO NA DETECÇÃO DE ALUCINAÇÕES")
    print("="*80)
    
    # TESTE A: SEM validação (mode = baseline)
    print("\n" + "▶️  INICIANDO TESTE A (SEM validação)...")
    print("-" * 80)
    
    test_a_output = ab_test_dir / f"test_a_results_{timestamp}"
    test_a_output.mkdir(exist_ok=True)
    
    # Executa com env var indicando Teste A
    env_a = os.environ.copy()
    env_a["SEXTANT_TEST_MODE"] = "test_a_no_validation"
    env_a["SEXTANT_OUTPUT_DIR"] = str(test_a_output)
    
    # Limpa audit_results para este teste
    audit_a_dir = test_a_output / "audit_results"
    audit_a_dir.mkdir(exist_ok=True)
    
    result_a = subprocess.run(
        ["python3", "sextant_main.py"],
        cwd=project_root,
        env=env_a,
        capture_output=False
    )
    
    if result_a.returncode != 0:
        print("❌ Teste A falhou!")
        sys.exit(1)
    
    # Copia resultados do Teste A
    audit_results_orig = project_root / "outputs" / "audit_results"
    if audit_results_orig.exists():
        for file in audit_results_orig.glob("*"):
            if file.name.startswith("audit_"):
                shutil.copy2(file, audit_a_dir)
                print(f"✓ Copiado: {file.name} -> Teste A")
    
    print("✅ Teste A completo!")
    
    # Limpa para Teste B
    print("\n" + "="*80)
    print("⏸️  Aguardando antes do Teste B...")
    print("-" * 80)
    
    # TESTE B: COM validação/ISR
    print("\n" + "▶️  INICIANDO TESTE B (COM validação + ISR)...")
    print("-" * 80)
    
    test_b_output = ab_test_dir / f"test_b_results_{timestamp}"
    test_b_output.mkdir(exist_ok=True)
    
    env_b = os.environ.copy()
    env_b["SEXTANT_TEST_MODE"] = "test_b_with_validation"
    env_b["SEXTANT_OUTPUT_DIR"] = str(test_b_output)
    
    audit_b_dir = test_b_output / "audit_results"
    audit_b_dir.mkdir(exist_ok=True)
    
    result_b = subprocess.run(
        ["python3", "sextant_main.py"],
        cwd=project_root,
        env=env_b,
        capture_output=False
    )
    
    if result_b.returncode != 0:
        print("❌ Teste B falhou!")
        sys.exit(1)
    
    # Copia resultados do Teste B
    if audit_results_orig.exists():
        for file in audit_results_orig.glob("*"):
            if file.name.startswith("audit_"):
                shutil.copy2(file, audit_b_dir)
                print(f"✓ Copiado: {file.name} -> Teste B")
    
    print("✅ Teste B completo!")
    
    # Gera comparação
    generate_comparison(test_a_output, test_b_output, ab_test_dir, timestamp)


def generate_comparison(test_a_dir, test_b_dir, output_dir, timestamp):
    """Compara resultados dos testes A e B"""
    
    print("\n" + "="*80)
    print("GERANDO RELATÓRIO COMPARATIVO...")
    print("="*80)
    
    import pandas as pd
    
    # Carrega CSVs
    csv_a = list((test_a_dir / "audit_results").glob("audit_results_*.csv"))
    csv_b = list((test_b_dir / "audit_results").glob("audit_results_*.csv"))
    
    if not csv_a or not csv_b:
        print("❌ CSVs de resultados não encontrados!")
        return
    
    df_a = pd.read_csv(csv_a[0])
    df_b = pd.read_csv(csv_b[0])
    
    # Calcula métricas
    def calc_metrics(df, name):
        total = len(df)
        passed = (df['status'] == 'PASS').sum()
        partial = (df['status'] == 'PARTIAL').sum()
        failed = (df['status'] == 'FAIL').sum()
        
        acuracia = (passed + partial) / total * 100 if total > 0 else 0
        isr_mean = df['isr'].astype(float).mean() if 'isr' in df.columns else 0
        acessibilidade = (df['acessivel'] == 'True').sum() / total * 100 if 'acessivel' in df.columns else 0
        
        return {
            "nome": name,
            "total": total,
            "pass": passed,
            "partial": partial,
            "fail": failed,
            "acuracia": acuracia,
            "isr_medio": isr_mean,
            "acessibilidade": acessibilidade
        }
    
    metrics_a = calc_metrics(df_a, "Teste A (SEM Validação)")
    metrics_b = calc_metrics(df_b, "Teste B (COM Validação)")
    
    # Gera relatório Markdown
    report_path = output_dir / f"AB_TEST_COMPARISON_{timestamp}.md"
    
    report = f"""# Relatório Comparativo: Teste A/B

**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Resumo

- **Teste A**: {metrics_a['total']} casos (SEM validação)
- **Teste B**: {metrics_b['total']} casos (COM validação + ISR)

## Comparação de Métricas

| Métrica | Teste A | Teste B | Delta | Melhoria |
|---------|---------|---------|-------|----------|
| **Acurácia** | {metrics_a['acuracia']:.2f}% | {metrics_b['acuracia']:.2f}% | {metrics_b['acuracia']-metrics_a['acuracia']:+.2f}% | {'✓' if metrics_b['acuracia'] > metrics_a['acuracia'] else '✗'} |
| **Pass** | {metrics_a['pass']} | {metrics_b['pass']} | {metrics_b['pass']-metrics_a['pass']:+d} | - |
| **Partial** | {metrics_a['partial']} | {metrics_b['partial']} | {metrics_b['partial']-metrics_a['partial']:+d} | - |
| **Fail** | {metrics_a['fail']} | {metrics_b['fail']} | {metrics_b['fail']-metrics_a['fail']:+d} | - |
| **ISR Médio** | N/A | {metrics_b['isr_medio']:.4f} | - | - |
| **Acessibilidade** | {metrics_a['acessibilidade']:.2f}% | {metrics_b['acessibilidade']:.2f}% | {metrics_b['acessibilidade']-metrics_a['acessibilidade']:+.2f}% | {'✓' if metrics_b['acessibilidade'] > metrics_a['acessibilidade'] else '✗'} |

## Análise Detalhada

### Impacto da Validação

**Acurácia:**
- Teste A (SEM validação): {metrics_a['acuracia']:.2f}%
- Teste B (COM validação): {metrics_b['acuracia']:.2f}%
- **Melhoria**: {metrics_b['acuracia']-metrics_a['acuracia']:+.2f}%

A validação {'MELHOROU' if metrics_b['acuracia'] > metrics_a['acuracia'] else 'PIOROU'} a acurácia do modelo.

### Qualidade das Explicações (ISR)

- **ISR Médio (Teste B)**: {metrics_b['isr_medio']:.4f}
- **Status**: {'✓ ADEQUADO (>0.85)' if metrics_b['isr_medio'] > 0.85 else '✗ INADEQUADO (<0.85)'}

O ISR está {'acima' if metrics_b['isr_medio'] > 0.85 else 'abaixo'} do threshold recomendado.

### Acessibilidade

- Teste A: {metrics_a['acessibilidade']:.2f}%
- Teste B: {metrics_b['acessibilidade']:.2f}%
- **Melhoria**: {metrics_b['acessibilidade']-metrics_a['acessibilidade']:+.2f}%

## Conclusões

1. **A validação ajuda a detectar alucinações?** 
   {'✓ SIM' if metrics_b['acuracia'] > metrics_a['acuracia'] else '✗ NÃO'} (melhoria de {abs(metrics_b['acuracia']-metrics_a['acuracia']):.2f}%)

2. **O ISR está adequado?**
   {'✓ SIM' if metrics_b['isr_medio'] > 0.85 else '✗ NÃO'} (valor: {metrics_b['isr_medio']:.4f})

3. **As respostas são acessíveis?**
   {'✓ Melhoraram' if metrics_b['acessibilidade'] > metrics_a['acessibilidade'] else '✗ Pioraram'} com validação

## Recomendações

"""
    
    if metrics_b['acuracia'] > metrics_a['acuracia']:
        report += "✓ **Incluir validação nos prompts** - Melhora detecção de erros\n"
    else:
        report += "✗ **Revisar estratégia de validação** - Não melhorou resultados\n"
    
    if metrics_b['isr_medio'] > 0.85:
        report += "✓ **Explicações são suficientes** - ISR acima de 0.85\n"
    else:
        report += "✗ **Melhorar qualidade das explicações** - ISR baixo\n"
    
    if metrics_b['acessibilidade'] > 50:
        report += "✓ **Acessibilidade aceitável** - Continue melhorando\n"
    else:
        report += "✗ **Melhorar acessibilidade** - Abaixo de 50%\n"
    
    # Salva relatório
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Relatório salvo: {report_path}\n")
    
    # Print summary
    print("="*80)
    print("RESULTADO FINAL DO TESTE A/B")
    print("="*80)
    print(f"\n📊 ACURÁCIA:")
    print(f"   Teste A (SEM validação): {metrics_a['acuracia']:.2f}%")
    print(f"   Teste B (COM validação): {metrics_b['acuracia']:.2f}%")
    print(f"   Diferença: {metrics_b['acuracia']-metrics_a['acuracia']:+.2f}%")
    
    print(f"\n📈 ISR MÉDIO:")
    print(f"   Teste B: {metrics_b['isr_medio']:.4f}")
    print(f"   Status: {'✓ ADEQUADO' if metrics_b['isr_medio'] > 0.85 else '✗ INADEQUADO'}")
    
    print(f"\n♿ ACESSIBILIDADE:")
    print(f"   Teste A: {metrics_a['acessibilidade']:.2f}%")
    print(f"   Teste B: {metrics_b['acessibilidade']:.2f}%")
    print(f"   Diferença: {metrics_b['acessibilidade']-metrics_a['acessibilidade']:+.2f}%")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    run_ab_test()
