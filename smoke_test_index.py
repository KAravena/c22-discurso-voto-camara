#!/usr/bin/env python3
from pathlib import Path
import re

path = Path(__file__).resolve().parent / "index.html"
content = path.read_text(encoding="utf-8")
assert path.exists(), "No existe index.html"
for link in [
    "seguridad_tbip_nominate.html",
    "trabajo_tbip_nominate.html",
    "salud_tbip_nominate.html",
    "educacion_tbip_nominate.html",
    "economia_tbip_nominate.html",
]:
    assert link in content, f"Falta link relativo: {link}"
for required in [
    "https://static.cepchile.cl/uploads/c22/2021/09/logo-color.svg",
    "https://static.cepchile.cl/uploads/c22/2021/09/logo-cep-color.svg",
    "c22-site-header",
    "c22-site-footer",
    "TBIP + NOMINATE",
    "discurso y votación en la Cámara",
    "Visualizadores temáticos",
    "Cómo leer este índice",
    "clamp(40px, 4.6vw, 66px)",
    "Seguridad pública",
    "Trabajo y empleo",
    "Sistema de salud",
    "Educación",
    "Economía y presupuesto",
    "temas legislativos",
    "parlamentarios comparados",
    "votaciones temáticas",
    "modelos discursivos TBIP",
    "390",
    "1.771",
]:
    assert required in content, f"Falta contenido requerido: {required}"
for forbidden in [
    "D:/CEP",
    "Metodología en breve",
    "Roadmap",
    "newsletter",
    "Hemiciclo de votaciones",
    "Análisis de votaciones",
    "Monitor de discurso legislativo",
    "NaN",
    "[object Object]",
    "Pearson r",
    "r = 0.",
    "casos ·",
    "relaciones comparadas",
    "visualizadores temáticos / ejes de debate",
    "visualizadores temáticos</div>",
    "class=\"chips\"",
    "class=\"tag\"",
    "hero-visual",
]:
    assert forbidden not in content, f"Contenido prohibido: {forbidden}"
assert content.count('class="stat"') == 4, "Cantidad inesperada de métricas"
assert content.count('<div class="stat-label">temas legislativos</div>') == 1, "Métrica temas legislativos repetida o ausente"
assert content.count('<div class="stat-label">parlamentarios comparados</div>') == 1, "Métrica parlamentarios repetida o ausente"
assert content.count('<div class="stat-label">votaciones temáticas</div>') == 1, "Métrica votaciones repetida o ausente"
assert content.count('<div class="stat-label">modelos discursivos TBIP</div>') == 1, "Métrica TBIP repetida o ausente"
for preview in re.findall(r'<div class="card-preview.*?</div>', content, flags=re.S):
    assert "<text" not in preview, "Preview contiene elemento SVG text"
    for label in ["SEGURIDAD", "TRABAJO", "SALUD", "EDUCACIÓN", "ECONOMÍA", "TBIP", "NOMINATE"]:
        assert label not in preview, f"Preview contiene texto interno: {label}"
print("Smoke test index OK")
