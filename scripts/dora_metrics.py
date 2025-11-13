#!/usr/bin/env python3
"""Generate lightweight DORA metrics from the local git repository.

This script does **not** reach external services. Instead it analyses the
current git history to produce indicative metrics that can be inspected in
JSON or Markdown form.  It intentionally favours transparency over
over-promising accuracy, keeping the values simple and reproducible offline.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Commit:
    sha: str
    timestamp: datetime
    subject: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcula métricas DORA usando únicamente el historial git local.",
    )
    parser.add_argument("--repo", help="Repositorio GitHub (solo para referencia)")
    parser.add_argument(
        "--days",
        type=int,
        help="Número de días hacia atrás a considerar (incompatible con --start/--end)",
    )
    parser.add_argument("--start", help="Fecha de inicio (YYYY-MM-DD)")
    parser.add_argument("--end", help="Fecha de fin (YYYY-MM-DD, inclusive)")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Formato de salida",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Archivo en el que guardar el resultado (stdout si se omite)",
    )
    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Limita el análisis a commits que tocan la carpeta docs/",
    )
    return parser.parse_args()


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw).replace(tzinfo=UTC)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise SystemExit(f"Fecha inválida: {raw}") from exc


def _compute_window(args: argparse.Namespace) -> tuple[datetime, datetime, int]:
    end = _parse_date(args.end) or datetime.now(UTC)
    if args.days:
        start = end - timedelta(days=args.days)
    else:
        start = _parse_date(args.start) or (end - timedelta(days=30))

    window_days = max(1, int((end - start).total_seconds() // 86400) or 1)
    return start, end, window_days


def _git_log(start: datetime, end: datetime, docs_only: bool) -> List[Commit]:
    pretty = "%H\x1f%ct\x1f%s\x1e"
    cmd = [
        "git",
        "log",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
        f"--pretty={pretty}",
    ]

    if docs_only:
        cmd.extend(["--", "docs/"])

    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if result.returncode != 0:  # pragma: no cover - git not available
        raise SystemExit(result.stderr.strip() or "git log failed")

    commits: List[Commit] = []
    for raw_commit in filter(None, result.stdout.split("\x1e")):
        parts = [piece for piece in raw_commit.strip().split("\x1f") if piece]
        if len(parts) < 3:
            continue
        sha, ts_raw, subject = parts[:3]
        commits.append(
            Commit(
                sha=sha,
                timestamp=datetime.fromtimestamp(int(ts_raw), tz=UTC),
                subject=subject,
            )
        )
    return commits


def _lead_time_stats(commits: Iterable[Commit], reference: datetime) -> dict:
    hours = [(reference - commit.timestamp).total_seconds() / 3600 for commit in commits]
    if not hours:
        return {
            "average_hours": 0.0,
            "median_hours": 0.0,
            "p95_hours": 0.0,
        }

    hours_sorted = sorted(hours)
    median = statistics.median(hours_sorted)
    p95 = hours_sorted[int(0.95 * (len(hours_sorted) - 1))] if len(hours_sorted) > 1 else hours_sorted[0]
    return {
        "average_hours": round(sum(hours_sorted) / len(hours_sorted), 2),
        "median_hours": round(median, 2),
        "p95_hours": round(p95, 2),
    }


def build_payload(args: argparse.Namespace) -> dict:
    start, end, window_days = _compute_window(args)
    commits = _git_log(start, end, docs_only=args.docs_only)
    reference = datetime.now(UTC)

    commit_count = len(commits)
    per_day = commit_count / window_days if window_days else 0
    per_week = per_day * 7

    lead_time = _lead_time_stats(commits, reference)

    payload = {
        "generated_at": reference.isoformat(),
        "scope": "docs" if args.docs_only else "repository",
        "analysis_window": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": window_days,
        },
        "deployment_frequency": {
            "count": commit_count,
            "per_day": round(per_day, 2),
            "per_week": round(per_week, 2),
        },
        "lead_time_for_changes": lead_time,
        "change_failure_rate": {
            "rate": None,
            "note": "Requiere integrar datos de incidentes reales",
        },
        "mean_time_to_recover": {
            "hours": None,
            "note": "No hay incidentes registrados en logs_data aún",
        },
        "notes": [
            "Datos inferidos desde git log (sin dependencias externas)",
            "Valores pensados como baseline provisional, no como métrica oficial",
        ],
    }
    return payload


def to_markdown(payload: dict) -> str:
    freq = payload["deployment_frequency"]
    lead = payload["lead_time_for_changes"]
    notes = payload["notes"]
    window = payload["analysis_window"]

    lines = [
        "# DORA Metrics Report",
        f"*Generated on*: {payload['generated_at']}",
        f"*Scope*: {payload['scope']}",
        f"*Window*: {window['start']} → {window['end']} ({window['days']} día(s))",
        "",
        "## Summary",
        f"- Deployment frequency: {freq['count']} commits (~{freq['per_week']:.2f} por semana)",
        f"- Lead time (mediana): {lead['median_hours']} h",
        "- Change failure rate: datos no disponibles",
        "- MTTR: datos no disponibles",
        "",
        "## Raw metrics",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Commits | {freq['count']} |",
        f"| Commits/día | {freq['per_day']:.2f} |",
        f"| Commits/semana | {freq['per_week']:.2f} |",
        f"| Lead time promedio (h) | {lead['average_hours']} |",
        f"| Lead time mediano (h) | {lead['median_hours']} |",
        f"| Lead time p95 (h) | {lead['p95_hours']} |",
        "| Change failure rate | Pendiente de instrumentar |",
        "| Mean time to recover | Pendiente de instrumentar |",
        "",
        "## Notes",
    ]

    for note in notes:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"


def output(payload: dict, args: argparse.Namespace) -> None:
    if args.format == "json":
        content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    else:
        content = to_markdown(payload)

    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    output(payload, args)


if __name__ == "__main__":
    main()
