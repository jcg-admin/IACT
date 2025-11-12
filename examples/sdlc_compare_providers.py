#!/usr/bin/env python3
"""
Ejemplo: Comparación de Proveedores LLM

Este script compara el análisis de la misma feature usando:
1. Heurísticas (sin LLM)
2. Ollama (local, open source)
3. Anthropic Claude (nube)
4. OpenAI GPT-4 (nube)

Útil para evaluar qué proveedor funciona mejor para tu caso de uso.

Uso:
    # Solo heurísticas y Ollama (no requiere API keys)
    python3 examples/sdlc_compare_providers.py

    # Incluir Claude y GPT-4 (requiere API keys en .env)
    export ANTHROPIC_API_KEY="..."
    export OPENAI_API_KEY="..."
    python3 examples/sdlc_compare_providers.py --all
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent


def analyze_with_provider(provider_name, config, issue):
    """
    Analiza una issue con un proveedor específico.

    Returns:
        tuple: (result, duration_seconds, error)
    """
    print(f"\n{'─'*70}")
    print(f"🔍 Analizando con: {provider_name}")
    print(f"{'─'*70}")

    try:
        start_time = time.time()

        agent = SDLCFeasibilityAgent(config=config)
        result = agent.run({"issue": issue})

        duration = time.time() - start_time

        print(f"✅ Completado en {duration:.2f}s")

        return result, duration, None

    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Error: {e}")
        return None, duration, str(e)


def main():
    """Compara proveedores LLM en la misma feature."""

    # Feature de complejidad media para comparar
    issue = {
        "title": "Implement Two-Factor Authentication (2FA)",
        "description": """
        Add two-factor authentication using TOTP (Time-based One-Time Password).
        Users should be able to enable/disable 2FA in their profile settings.

        Flow:
        1. User enables 2FA in settings
        2. System generates QR code with secret
        3. User scans QR code with authenticator app (Google Authenticator, Authy)
        4. User enters 6-digit code to confirm
        5. On subsequent logins, user must provide 6-digit code after password

        Security requirements:
        - Store secret encrypted in database
        - Generate backup codes (10 single-use codes)
        - Allow 2FA reset via email (with security review)
        - Rate limit 2FA verification attempts
        """,
        "requirements": [
            "TOTP library integration (pyotp)",
            "QR code generation",
            "Encrypted secret storage",
            "Backup codes generation (10 codes)",
            "2FA verification middleware",
            "Email-based 2FA reset",
            "Rate limiting (max 3 attempts per 5 minutes)",
            "Admin panel to disable 2FA for users (emergency)"
        ],
        "acceptance_criteria": [
            "Users can enable 2FA with QR code",
            "Users can disable 2FA with current 2FA code",
            "Backup codes work for login",
            "Invalid 2FA codes are rejected",
            "Rate limiting prevents brute force",
            "Email reset works with security confirmation",
            "Tests coverage >85%"
        ],
        "estimated_story_points": 8
    }

    print("\n" + "="*70)
    print("🔬 COMPARACIÓN DE PROVEEDORES LLM")
    print("="*70)
    print(f"\n📋 Feature: {issue['title']}")
    print(f"📊 Story Points: {issue['estimated_story_points']}")
    print(f"📝 Requirements: {len(issue['requirements'])}")
    print(f"✅ Acceptance Criteria: {len(issue['acceptance_criteria'])}")

    results = {}

    # 1. Heurísticas (sin LLM) - SIEMPRE disponible
    print("\n" + "="*70)
    print("1️⃣  HEURÍSTICAS (Sin LLM)")
    print("="*70)
    print("💰 Costo: Gratis")
    print("🌐 Privacidad: Total (local)")
    print("⚡ Velocidad: Muy rápida")

    result, duration, error = analyze_with_provider(
        "Heurísticas",
        config=None,
        issue=issue
    )
    results['heuristic'] = (result, duration, error)

    # 2. Ollama (local) - Disponible si Ollama está corriendo
    print("\n" + "="*70)
    print("2️⃣  OLLAMA (Local Open Source)")
    print("="*70)
    print("💰 Costo: Gratis")
    print("🌐 Privacidad: Total (local)")
    print("⚡ Velocidad: Media-Lenta (depende de hardware)")
    print("🖥️  Modelo: llama3.1:8b")

    ollama_config = {
        "llm_provider": "ollama",
        "model": "llama3.1:8b",
        "ollama_base_url": "http://localhost:11434",
        "use_llm": True
    }

    result, duration, error = analyze_with_provider(
        "Ollama (llama3.1:8b)",
        config=ollama_config,
        issue=issue
    )
    results['ollama'] = (result, duration, error)

    # 3. Anthropic Claude - Solo si API key está disponible
    if os.getenv("ANTHROPIC_API_KEY") and "--all" in sys.argv:
        print("\n" + "="*70)
        print("3️⃣  ANTHROPIC CLAUDE")
        print("="*70)
        print("💰 Costo: ~$0.003 por request")
        print("🌐 Privacidad: Cloud (Anthropic)")
        print("⚡ Velocidad: Rápida")
        print("🤖 Modelo: claude-3-5-sonnet")

        claude_config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "use_llm": True
        }

        result, duration, error = analyze_with_provider(
            "Anthropic Claude",
            config=claude_config,
            issue=issue
        )
        results['anthropic'] = (result, duration, error)
    else:
        print("\n" + "="*70)
        print("3️⃣  ANTHROPIC CLAUDE - SKIPPED")
        print("="*70)
        print("ℹ️  Set ANTHROPIC_API_KEY y ejecuta con --all para incluir")

    # 4. OpenAI GPT-4 - Solo si API key está disponible
    if os.getenv("OPENAI_API_KEY") and "--all" in sys.argv:
        print("\n" + "="*70)
        print("4️⃣  OPENAI GPT-4")
        print("="*70)
        print("💰 Costo: ~$0.005 por request")
        print("🌐 Privacidad: Cloud (OpenAI)")
        print("⚡ Velocidad: Rápida")
        print("🤖 Modelo: gpt-4-turbo")

        openai_config = {
            "llm_provider": "openai",
            "model": "gpt-4-turbo-preview",
            "use_llm": True
        }

        result, duration, error = analyze_with_provider(
            "OpenAI GPT-4",
            config=openai_config,
            issue=issue
        )
        results['openai'] = (result, duration, error)
    else:
        print("\n" + "="*70)
        print("4️⃣  OPENAI GPT-4 - SKIPPED")
        print("="*70)
        print("ℹ️  Set OPENAI_API_KEY y ejecuta con --all para incluir")

    # COMPARACIÓN DE RESULTADOS
    print("\n" + "="*70)
    print("📊 TABLA COMPARATIVA")
    print("="*70 + "\n")

    # Header
    print(f"{'Proveedor':<20} {'Decisión':<12} {'Conf.':<8} {'Riesgos':<10} "
          f"{'Tiempo':<10} {'Status'}")
    print("─" * 80)

    # Rows
    provider_names = {
        'heuristic': 'Heurísticas',
        'ollama': 'Ollama (llama3.1)',
        'anthropic': 'Anthropic Claude',
        'openai': 'OpenAI GPT-4'
    }

    for key, name in provider_names.items():
        if key in results:
            result, duration, error = results[key]

            if result:
                decision = result.decision.upper()
                confidence = f"{result.confidence:.1%}"
                num_risks = len(result.risks)
                time_str = f"{duration:.2f}s"
                status = "✅"

                # Color coding for decision
                if decision == "GO":
                    decision_display = f"✅ {decision}"
                elif decision == "NO-GO":
                    decision_display = f"❌ {decision}"
                else:
                    decision_display = f"⚠️ {decision}"

                print(f"{name:<20} {decision_display:<12} {confidence:<8} "
                      f"{num_risks:<10} {time_str:<10} {status}")
            else:
                print(f"{name:<20} {'ERROR':<12} {'N/A':<8} {'N/A':<10} "
                      f"{duration:.2f}s {'❌':<10} {error[:30]}")

    # ANÁLISIS DETALLADO DE DIFERENCIAS
    print("\n" + "="*70)
    print("🔍 ANÁLISIS DETALLADO")
    print("="*70 + "\n")

    # Comparar número de riesgos identificados
    print("⚠️  Riesgos Identificados:")
    for key, name in provider_names.items():
        if key in results and results[key][0]:
            result = results[key][0]
            risks_by_severity = {}
            for risk in result.risks:
                sev = risk.get('severity', 'unknown')
                risks_by_severity[sev] = risks_by_severity.get(sev, 0) + 1

            risk_str = ", ".join([f"{sev}: {count}" for sev, count in risks_by_severity.items()])
            print(f"   {name:<20} → Total: {len(result.risks):2d} ({risk_str})")

    # Comparar confianza
    print("\n🎯 Niveles de Confianza:")
    for key, name in provider_names.items():
        if key in results and results[key][0]:
            result = results[key][0]
            conf = result.confidence
            bar = "█" * int(conf * 20)
            print(f"   {name:<20} → {conf:.1%} {bar}")

    # Comparar velocidad
    print("\n⚡ Velocidad de Análisis:")
    for key, name in provider_names.items():
        if key in results and results[key][1]:
            duration = results[key][1]
            bar_len = min(int(duration / 0.5), 50)  # 0.5s por bloque
            bar = "█" * bar_len
            print(f"   {name:<20} → {duration:5.2f}s {bar}")

    # Recomendaciones
    print("\n" + "="*70)
    print("💡 RECOMENDACIONES")
    print("="*70 + "\n")

    print("✅ Usa HEURÍSTICAS si:")
    print("   - Necesitas análisis instantáneo (<0.1s)")
    print("   - La feature es simple y bien definida")
    print("   - No tienes acceso a LLM o API keys")
    print("   - Quieres análisis 100% reproducible")

    print("\n✅ Usa OLLAMA si:")
    print("   - Quieres análisis mejorado sin costo")
    print("   - Tienes hardware decente (16GB+ RAM)")
    print("   - Privacidad es crítica (no enviar datos a cloud)")
    print("   - Estás en desarrollo/testing")

    print("\n✅ Usa CLAUDE si:")
    print("   - Necesitas el mejor análisis posible")
    print("   - La feature es compleja o ambigua")
    print("   - Presupuesto permite ($0.003/request)")
    print("   - Velocidad es importante")

    print("\n✅ Usa GPT-4 si:")
    print("   - Ya tienes infraestructura OpenAI")
    print("   - Quieres análisis muy detallado")
    print("   - Presupuesto permite ($0.005/request)")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
