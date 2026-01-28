#!/usr/bin/env python3
"""
Script de visualização dos resultados do Teste A/B
Mostra métricas, gráficos de comparação e recomendações
"""

import json
import os
from pathlib import Path
from datetime import datetime

def display_ab_results():
    """Exibe resultados do teste A/B"""
    
    project_root = Path(__file__).parent
    ab_test_dir = project_root / "outputs" / "ab_test"
    
    print("\n" + "="*90)
    print("🔬 RESULTADOS DO TESTE A/B: IMPACTO DA VALIDAÇÃO NA DETECÇÃO DE ALUCINAÇÕES".center(90))
    print("="*90)
    
    # Tenta carregar o JSON mais recente
    json_files = sorted(ab_test_dir.glob("AB_COMPARISON_*.json"))
    if not json_files:
        print("\n❌ Nenhum arquivo de resultados encontrado!")
        return
    
    latest_json = json_files[-1]
    with open(latest_json, 'r') as f:
        data = json.load(f)
    
    metrics = data['metricas']
    status = data['status']
    
    # Header
    print(f"\n📊 EXECUTADO: {data['timestamp']}")
    print(f"📁 ARQUIVO: {data['arquivo_origem']}")
    print(f"⏱️  TOTAL: {metrics['total']} casos × ~20s = {metrics['total']*20//60}m {metrics['total']*20%60}s")
    
    # Metrics Dashboard
    print("\n" + "-"*90)
    print("📈 MÉTRICAS DE DESEMPENHO".ljust(90))
    print("-"*90)
    
    # Acurácia
    acc = metrics['acuracia']
    bar_acc = "█" * int(acc/5) + "░" * (20 - int(acc/5))
    status_acc = "✅ OK" if status['acuracia_ok'] else "❌ CRÍTICO"
    print(f"\n  Acurácia: {bar_acc} {acc:6.2f}% {status_acc} (Target: >80%)")
    
    # Recall
    recall = metrics['recall']
    bar_recall = "█" * int(recall/5) + "░" * (20 - int(recall/5))
    status_recall = "✅ OK" if status['recall_ok'] else "❌ CRÍTICO"
    print(f"  Recall:   {bar_recall} {recall:6.2f}% {status_recall} (Target: >80%)")
    
    # ISR
    isr = metrics['isr_medio']
    bar_isr = "█" * int(isr*20) + "░" * (20 - int(isr*20))
    status_isr = "✅ OK" if status['isr_ok'] else "⚠️  BAIXO"
    print(f"  ISR:      {bar_isr} {isr:6.4f}  {status_isr} (Target: >0.85)")
    
    # Acessibilidade
    acess = metrics['acessibilidade']
    bar_acess = "█" * int(acess/5) + "░" * (20 - int(acess/5))
    status_acess = "✅ OK" if status['acessibilidade_ok'] else "❌ CRÍTICO"
    print(f"  Acessibilidade: {bar_acess} {acess:6.2f}% {status_acess} (Target: >70%)")
    
    # Confiança
    conf = metrics['confianca_media']
    bar_conf = "█" * int(conf*20) + "░" * (20 - int(conf*20))
    print(f"  Confiança: {bar_conf} {conf:6.4f} (Current)")
    
    # Resultados
    print("\n" + "-"*90)
    print("📋 DISTRIBUIÇÃO DE RESULTADOS".ljust(90))
    print("-"*90)
    
    total = metrics['total']
    passed = metrics['passed']
    partial = metrics['partial']
    failed = metrics['failed']
    
    print(f"\n  PASS (Aprovado):   {passed:2d} casos | {'█'*int(passed/total*50):<50} {passed/total*100:5.1f}%")
    print(f"  PARTIAL (Parcial): {partial:2d} casos | {'█'*int(partial/total*50):<50} {partial/total*100:5.1f}%")
    print(f"  FAIL (Reprovado):  {failed:2d} casos | {'█'*int(failed/total*50):<50} {failed/total*100:5.1f}%")
    
    # Status Overall
    print("\n" + "-"*90)
    print("🎯 STATUS GERAL".ljust(90))
    print("-"*90)
    
    passed_tests = sum(1 for v in status.values() if v)
    total_tests = len(status)
    
    print(f"\n  Testes Passando: {passed_tests}/{total_tests}")
    
    if status['acuracia_ok']:
        print("    ✅ Acurácia aceitável")
    else:
        print("    ❌ Acurácia CRÍTICA - Modelo rejeita >92% dos casos")
    
    if status['recall_ok']:
        print("    ✅ Detecção de erros efetiva")
    else:
        print("    ❌ Detecção de erros FALHOU - 0% de casos identificados")
    
    if status['isr_ok']:
        print("    ✅ Explicações suficientemente detalhadas")
    else:
        print("    ⚠️  Explicações INSUFICIENTES - ISR abaixo do esperado")
    
    if status['acessibilidade_ok']:
        print("    ✅ Respostas acessíveis")
    else:
        print("    ❌ Respostas NÃO ACESSÍVEIS - Linguagem muito técnica")
    
    # Recomendações
    print("\n" + "-"*90)
    print("💡 RECOMENDAÇÕES IMEDIATAS".ljust(90))
    print("-"*90)
    
    print("\n  1️⃣  CRÍTICA - Reescrever Prompt")
    print("      • Adicionar detecção explícita de alucinações")
    print("      • Incluir matriz de validação no contexto")
    print("      • Solicitar formato estruturado (JSON)")
    print("      • Incluir exemplos de alucinações esperadas")
    
    print("\n  2️⃣  IMPORTANTE - Otimizar ISR")
    print("      • ISR atual: 0.248 (INADEQUADO)")
    print("      • Adicionar requisitos de rastreabilidade")
    print("      • Forçar referências às políticas")
    print("      • Validar suficiência de informação")
    
    print("\n  3️⃣  IMPORTANTE - Melhorar Recall")
    print("      • Recall atual: 0% (CRÍTICO)")
    print("      • Implementar detecção bináría (erro/ok)")
    print("      • Testar com exemplos simples primeiro")
    print("      • Medir Recall em versão otimizada")
    
    print("\n  4️⃣  DESEJÁVEL - Aumentar Acessibilidade")
    print("      • Adicionar explicações em linguagem clara")
    print("      • Estruturar com bullets e seções")
    print("      • Usar analogias simples")
    print("      • Reduzir jargão técnico")
    
    # Próximos Passos
    print("\n" + "-"*90)
    print("📍 PRÓXIMOS PASSOS".ljust(90))
    print("-"*90)
    
    print("\n  ➡️  Fase 1 (Hoje):    Diagnóstico ✅ COMPLETO")
    print("      └─ Identificar problema: Acurácia 8%, ISR 0.248")
    
    print("\n  ➡️  Fase 2 (Próxima): Otimização (48-72 horas)")
    print("      ├─ Reescrever prompt com detecção de alucinações")
    print("      ├─ Adicionar matriz de validação")
    print("      ├─ Executar Teste B com 5 casos (quick test)")
    print("      └─ Comparar ISR Teste B vs Teste A")
    
    print("\n  ➡️  Fase 3:           Validação (5 dias)")
    print("      ├─ Escalar para 25 casos")
    print("      ├─ Medir Recall real")
    print("      ├─ Validar conformidade")
    print("      └─ Implementar em staging")
    
    print("\n  ➡️  Fase 4:           Produção (7-10 dias)")
    print("      ├─ Deploy em produção")
    print("      ├─ Monitoramento contínuo")
    print("      ├─ Ajuste de thresholds")
    print("      └─ Manutenção operacional")
    
    # Conclusão
    print("\n" + "="*90)
    print("🎯 CONCLUSÃO".center(90))
    print("="*90)
    
    if passed_tests <= 1:
        print("\n  ⚠️  STATUS: CRÍTICO - Modelo não está operacional")
        print("  📊 Razão: Apenas 1/4 métricas dentro do esperado")
        print("  🔧 Ação: Reescrever prompt HOJE")
        print("  ⏱️  Timeline: Teste B em 48 horas")
    elif passed_tests <= 2:
        print("\n  ⚠️  STATUS: INADEQUADO - Requer otimizações")
        print("  📊 Razão: Apenas 2/4 métricas aceitáveis")
        print("  🔧 Ação: Implementar melhorias esta semana")
    else:
        print("\n  ✅ STATUS: ADEQUADO - Pronto para escalação")
    
    print("\n" + "="*90 + "\n")


if __name__ == "__main__":
    display_ab_results()
