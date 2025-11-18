"""
Analizador de contenido para extracción dinámica de keywords.

Extrae términos técnicos característicos de cada dominio
mediante análisis de frecuencia de términos.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

from .structure_discovery import ProjectStructureDiscovery


class DomainContentAnalyzer:
    """Analiza contenido de dominios para extraer keywords."""

    # Palabras comunes a ignorar (stopwords técnicas)
    STOPWORDS = {
        # Palabras comunes en español
        "el",
        "la",
        "de",
        "que",
        "y",
        "a",
        "en",
        "un",
        "ser",
        "se",
        "no",
        "para",
        "con",
        "por",
        "su",
        "al",
        "los",
        "del",
        "una",
        "es",
        # Palabras comunes en inglés
        "the",
        "be",
        "to",
        "of",
        "and",
        "a",
        "in",
        "that",
        "have",
        "i",
        "it",
        "for",
        "not",
        "on",
        "with",
        "he",
        "as",
        "you",
        "do",
        "at",
        "this",
        "but",
        "his",
        "by",
        "from",
        # Palabras técnicas genéricas
        "system",
        "module",
        "function",
        "class",
        "method",
        "file",
        "directory",
        "documento",
        "archivo",
        "código",
        "code",
    }

    def __init__(self, project_root: str = None):
        """
        Inicializa el analizador de contenido.

        Args:
            project_root: Ruta raíz del proyecto
        """
        self.discovery = ProjectStructureDiscovery(project_root)
        self._keyword_cache = {}

    def extract_technical_terms(self, content: str) -> List[str]:
        """
        Extrae términos técnicos de un contenido.

        Args:
            content: Contenido a analizar

        Returns:
            Lista de términos técnicos encontrados
        """
        # Normalizar a lowercase
        content_lower = content.lower()

        # Extraer términos de 3+ caracteres (palabras completas)
        # Incluir términos con guiones (ej: "rest-api", "machine-learning")
        words = re.findall(r"\b[a-z][a-z0-9\-]{2,}\b", content_lower)

        # Filtrar stopwords
        terms = [w for w in words if w not in self.STOPWORDS]

        # También extraer frases técnicas comunes (bigramas)
        bigrams = self._extract_bigrams(content_lower)

        return terms + bigrams

    def _extract_bigrams(self, content: str) -> List[str]:
        """
        Extrae bigramas técnicos (ej: "rest api", "machine learning").

        Args:
            content: Contenido en lowercase

        Returns:
            Lista de bigramas
        """
        # Patrones conocidos de bigramas técnicos
        TECHNICAL_PATTERNS = [
            r"\b(rest|graphql|grpc)\s+(api|endpoint|service)\b",
            r"\b(machine|deep)\s+learning\b",
            r"\b(neural|convolutional)\s+network\b",
            r"\b(docker|kubernetes|jenkins)\s+(container|image|pipeline)\b",
            r"\b(react|vue|angular)\s+(component|hook|directive)\b",
            r"\b(django|flask|fastapi)\s+(rest|framework|orm)\b",
            r"\b(postgresql|mysql|mongodb)\s+(database|query)\b",
            r"\b(ci|cd)\s*\/?\s*(cd|pipeline)\b",
        ]

        bigrams = []
        for pattern in TECHNICAL_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                # Unir tupla a string
                if isinstance(match, tuple):
                    bigram = " ".join(match)
                else:
                    bigram = match
                bigrams.append(bigram.replace("/", ""))

        return bigrams

    def analyze_domain_keywords(
        self, domain: str, top_n: int = 20
    ) -> List[str]:
        """
        Analiza archivos de un dominio y extrae keywords más frecuentes.

        Args:
            domain: Nombre del dominio
            top_n: Número de keywords a retornar

        Returns:
            Lista de keywords más representativas del dominio
        """
        # Usar cache si existe
        cache_key = f"{domain}:{top_n}"
        if cache_key in self._keyword_cache:
            return self._keyword_cache[cache_key]

        # Obtener archivos del dominio
        files = self.discovery.get_domain_files(domain, extensions={".md"})

        if not files:
            return []

        # Contador de términos
        term_counter = Counter()

        # Analizar cada archivo
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                terms = self.extract_technical_terms(content)
                term_counter.update(terms)
            except (UnicodeDecodeError, PermissionError):
                # Ignorar archivos que no se pueden leer
                continue

        # Obtener top N términos
        keywords = [term for term, count in term_counter.most_common(top_n)]

        # Cachear resultado
        self._keyword_cache[cache_key] = keywords

        return keywords

    def build_domain_keyword_map(self, top_n: int = 15) -> Dict[str, List[str]]:
        """
        Construye mapa de keywords por dominio.

        Args:
            top_n: Número de keywords por dominio

        Returns:
            Diccionario {dominio: [keywords]}

        Example:
            {
                'backend': ['django', 'rest api', 'postgresql', ...],
                'frontend': ['react', 'typescript', 'component', ...],
            }
        """
        structure = self.discovery.build_structure_map()
        domains = structure["domains"].keys()

        keyword_map = {}
        for domain in domains:
            keywords = self.analyze_domain_keywords(domain, top_n)
            keyword_map[domain] = keywords

        return keyword_map

    def detect_domains_in_content(
        self,
        content: str,
        keyword_map: Dict[str, List[str]] = None,
        min_matches: int = None,
    ) -> List[str]:
        """
        Detecta qué dominios se mencionan en un contenido.

        Args:
            content: Contenido a analizar
            keyword_map: Mapa de keywords por dominio (se genera si None)
            min_matches: Mínimo de keywords para detectar dominio
                        (usa config si None)

        Returns:
            Lista de dominios detectados
        """
        if keyword_map is None:
            keyword_map = self.build_domain_keyword_map()

        if min_matches is None:
            # Usar threshold del config
            from .config_loader import PlacementConfig

            config = PlacementConfig()
            min_matches = config.get_min_keywords_for_detection()

        content_lower = content.lower()
        detected_domains = []

        for domain, keywords in keyword_map.items():
            # Contar cuántas keywords del dominio aparecen
            matches = sum(1 for kw in keywords if kw in content_lower)

            # Si al menos min_matches keywords coinciden, detectar dominio
            if matches >= min_matches:
                detected_domains.append(domain)

        return detected_domains


def main():
    """Ejemplo de uso del analizador."""
    analyzer = DomainContentAnalyzer()

    print("Análisis de keywords por dominio:")
    print("=" * 60)

    keyword_map = analyzer.build_domain_keyword_map(top_n=10)

    for domain, keywords in keyword_map.items():
        print(f"\n{domain}:")
        for kw in keywords:
            print(f"  - {kw}")

    # Ejemplo de detección
    print("\n\nEjemplo de detección:")
    print("=" * 60)

    test_content = """
    Esta guía explica cómo configurar Django REST Framework
    con PostgreSQL para crear una API REST robusta.
    """

    detected = analyzer.detect_domains_in_content(test_content, keyword_map)
    print(f"\nContenido: {test_content.strip()}")
    print(f"Dominios detectados: {detected}")


if __name__ == "__main__":
    main()
