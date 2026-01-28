#!/usr/bin/env python3
"""
Script para comparar métricas dos testes A/B
Analisa resultados já gerados e calcula métricas de impacto
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def calculate_ab_metrics():
    """Calcula e compara métricas de teste A/B"""
    
    # Busca último relatório gerado
    audit_results_dir = Path("outputs/audit_results")
    if not audit_results_dir.exists():
        print("❌ Nenhum resultado de auditoria encontrado!")
        return
    
    # Encontra último CSV
    csv_files = list(audit_results_dir.glob("audit_results_*.csv"))
    if not csv_files:
        print("❌ Nenhum arquivo de resultados encontrado!")
        return
    
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📂 Carregando resultados de: {latest_csv.name}")
    
    # Lê CSV
    import pandas as pd
    df = pd.read_csv(latest_csv)
    
    # Calcula métricas
    print("\n" + "="*80)
    print("MÉTRICAS DE DESEMPENHO - TESTE A/B")
    print("="*80)
    
    total = len(df)
    passed = (df['status'] == 'PASS').sum()
    failed = (df['status'] == 'FAIL').sum()
    partial = (df['status'] == 'PARTIAL').sum()
    
    # Acurácia
    acurácia = (passed + partial) / total * 100 if total > 0 else 0
    print(f"\n📊 ACURÁCIA: {acurácia:.2f}%")
    print(f"   ✓ Pass:    {passed}")
    print(f"   ◐ Partial: {partial}")
    print(f"   ✗ Fail:    {failed}")
    
    # Recall (quantos erros foram detectados?)
    if 'tipo_cenario' in df.columns:
        alucinacoes = df[df['tipo_cenario'] == 'alucinacao']
        if len(alucinacoes) > 0:
            alucinacao_detected = ((alucinacoes['status'] == 'FAIL') | (alucinacoes['status'] == 'PARTIAL')).sum()
            recall = alucinacao_detected / len(alucinacoes) * 100
            print(f"\n🎯 RECALL (Detecção de Alucinações): {recall:.2f}%")
            print(f"   Detectou {alucinacao_detected}/{len(alucinacoes)} alucinações")
    
    # ISR Médio
    if 'isr' in df.columns:
        isr_mean = df['isr'].astype(float).mean()
        print(f"\n📈 ISR MÉDIO: {isr_mean:.4f}")
        print(f"   Status: {'✓ ADEQUADO (>0.85)' if isr_mean > 0.85 else '✗ INADEQUADO'}")
    else:
        print(f"\n⚠️  ISR não disponível neste relatório")
    
    # Acessibilidade
    if 'acessivel' in df.columns:
        acessibilidade = (df['acessivel'] == 'True').sum() / total * 100
        print(f"\n♿ ACESSIBILIDADE: {acessibilidade:.2f}%")
    
    print("\n" + "="*80)
    print("\n💡 RECOMENDAÇÕES:")
    
    if acurácia < 50:
        print("   1. Acurácia muito baixa - Revisar prompt/modelo")
    if recall < 50 and 'tipo_cenario' in df.columns:
        print("   2. Recall baixo - ISR não está detectando erros adequadamente")
    
    print("\n✅ Análise concluída!\n")


if __name__ == "__main__":
    calculate_ab_metrics()
