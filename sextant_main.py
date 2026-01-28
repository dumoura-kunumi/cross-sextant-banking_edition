"""
Main entry point para Sextant Banking Edition.
Versão 2.0 - Com suporte a modo mock.
"""
import asyncio
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.core.fsm import SextantFSM
from src.utils.logger import setup_logger
from src.utils.config import settings


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sextant Banking Edition - Framework de Auditoria de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python sextant_main.py                    # Modo mock (padrão, rápido)
  python sextant_main.py --mock             # Modo mock explícito
  python sextant_main.py --real             # Modo API real (requer API key)
  python sextant_main.py --num-cases 10     # Limita a 10 casos
  python sextant_main.py --mock --num-cases 25 --verbose
        """
    )

    # Modo de execução
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--mock',
        action='store_true',
        default=True,
        help='Use mock responses (padrão, não requer API key)'
    )
    mode_group.add_argument(
        '--real',
        action='store_true',
        help='Use real API calls (requer ANTHROPIC_API_KEY ou OPENAI_API_KEY)'
    )

    # Configurações
    parser.add_argument(
        '--num-cases', '-n',
        type=int,
        default=None,
        help='Número máximo de casos a processar (default: todos)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Ativa logs detalhados'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default=None,
        help='Diretório de saída para relatórios'
    )
    parser.add_argument(
        '--data-dir', '-d',
        type=str,
        default=None,
        help='Diretório com dados de entrada (clientes, casos, políticas)'
    )
    parser.add_argument(
        '--test-clients',
        type=str,
        default=None,
        help='Arquivo JSON com clientes de teste (ex: clientes_teste_mock.json)'
    )

    return parser.parse_args()


def main():
    """
    Executa Sextant Banking Edition - Framework de Auditoria de IA.

    Modos:
        --mock (padrão): Usa respostas simuladas, rápido, sem API
        --real: Usa API real (Anthropic ou OpenAI)

    Exemplo:
        python sextant_main.py --mock --num-cases 25
        python sextant_main.py --real --num-cases 5
    """
    args = parse_args()

    # Determina modo
    use_mock = not args.real

    logger = setup_logger("sextant_main", verbose=args.verbose if hasattr(args, 'verbose') else False)

    logger.info("=" * 70)
    logger.info("SEXTANT BANKING EDITION - Framework de Auditoria de IA")
    logger.info("=" * 70)
    logger.info(f"Modo: {'MOCK (simulado)' if use_mock else 'REAL (API)'}")

    # Valida configurações para modo real
    if not use_mock:
        if settings.MODEL_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
            logger.error("ANTHROPIC_API_KEY não configurada. Configure no .env")
            logger.error("Para testes sem API, use: python sextant_main.py --mock")
            sys.exit(1)

        if settings.MODEL_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY não configurada. Configure no .env")
            logger.error("Para testes sem API, use: python sextant_main.py --mock")
            sys.exit(1)
    else:
        logger.info("Modo MOCK: Não requer API key")

    # Cria FSM e configura contexto
    fsm = SextantFSM()

    # Configurações de diretório
    fsm.context["data_dir"] = Path(args.data_dir) if args.data_dir else settings.DATA_DIR
    fsm.context["output_dir"] = Path(args.output_dir) if args.output_dir else settings.OUTPUT_DIR

    # Configurações de execução
    fsm.context["use_mock"] = use_mock

    if args.num_cases:
        fsm.context["num_cases"] = args.num_cases
        logger.info(f"Limitando a {args.num_cases} casos")

    if args.test_clients:
        fsm.context["test_clients_file"] = args.test_clients
        logger.info(f"Usando clientes de teste: {args.test_clients}")

    try:
        asyncio.run(fsm.run())
        logger.info("Sextant completed successfully")

        # Mostra caminho do relatório
        report_path = fsm.context.get("report_path")
        if report_path:
            logger.info(f"Report available at: {report_path}")

        # Mostra métricas resumidas
        metricas = fsm.context.get("metricas")
        if metricas:
            logger.info("-" * 50)
            logger.info("RESUMO DAS MÉTRICAS:")
            logger.info(f"  Taxa de Acerto: {metricas.taxa_acerto:.1%}")
            logger.info(f"  Taxa de Acessibilidade: {metricas.taxa_acessibilidade:.1%}")
            logger.info(f"  ISR Médio: {metricas.isr_medio:.2f}")
            logger.info(f"  Casos PASS: {metricas.casos_pass}")
            logger.info(f"  Casos PARTIAL: {metricas.casos_partial}")
            logger.info(f"  Casos FAIL: {metricas.casos_fail}")
            logger.info("-" * 50)

        return 0
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Sextant failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
