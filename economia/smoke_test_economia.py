#!/usr/bin/env python3
import json
import re
from pathlib import Path

html_path = Path(r"D:\CEP\Mar - intervenciones\Nominate\web_tematicos\economia_tbip_nominate.html")
text = html_path.read_text(encoding="utf-8")
assert html_path.exists(), "HTML no existe"
for marker in ['hero', 'metrics-row', 'visualizer-wrapper', 'visualizer-tabs-container', 'tab-tbip', 'tab-nominate', 'tab-compare', 'tab-pactos', 'tab-topics', 'visualizer-chart', 'synthesis-grid-content', 'highlight-grid', 'methodology-section', 'deputy-sidebar', 'const DATA']:
    assert marker in text, f"Falta marcador del template: {marker}"
if "economia" != "seguridad":
    assert "Seguridad en la Cámara: discurso y votación" not in text, "Quedó título fijo de seguridad"
assert "Economía en la Cámara: discurso y votación" in text, "No aparece título correcto"
for required in [
    "c22-site-header",
    "c22-site-footer",
    "https://static.cepchile.cl/uploads/c22/2021/09/logo-color.svg",
    "https://static.cepchile.cl/uploads/c22/2021/09/logo-cep-color.svg",
    "index.html",
    "const DATA",
    "visualizer-wrapper",
    "tab-tbip",
    "tab-nominate",
    "tab-compare",
    "tab-pactos",
    "tab-topics",
]:
    assert required in text, f"Falta contenido C22/template: {required}"
assert "global-visual-zoom-override" in text, "No está inyectado el override de zoom"
assert "zoom: 0.8" in text, "No está aplicado zoom: 0.8"
assert "NaN" not in text, "HTML contiene NaN"
assert "[object Object]" not in text, "HTML contiene [object Object]"
match = re.search(r"<script>const DATA = (.*?);</script>", text, re.S)
assert match, "No se pudo extraer DATA"
data = json.loads(match.group(1))
assert data["theme"] == "economia", "DATA.theme no coincide"
assert len(data.get("members", [])) > 0, "DATA.members sin casos"
assert len(data.get("matched", [])) > 0, "DATA.matched sin casos"
if "economia" != "seguridad":
    assert "sin clasificar" not in text, "Aparece 'sin clasificar' en tópicos"
    assert "Etiqueta automática. Revisar manualmente." not in text, "Aparece etiqueta automática genérica"
    assert any(status in text for status in ["principal", "secundario", "exploratorio"]), "No aparece status descriptivo de tópicos"
else:
    assert "Migración, frontera norte y control irregular" in text, "No se conservaron etiquetas manuales de seguridad"
print("Smoke test OK: economia")
