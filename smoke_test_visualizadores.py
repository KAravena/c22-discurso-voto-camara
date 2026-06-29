#!/usr/bin/env python3
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
THEMES = ["seguridad", "trabajo", "salud", "educacion", "economia"]
REQUIRED = [
    "const DATA",
    "members",
    "matched",
    "nominate_all",
    "topics",
    "visualizer-wrapper",
    "visualizer-chart",
    "tab-tbip",
    "tab-nominate",
    "tab-compare",
    "tab-pactos",
    "tab-topics",
]


def parse_data(text: str) -> dict:
    match = re.search(r"<script>const DATA = (.*?);</script>", text, re.S)
    if not match:
        raise AssertionError("No se pudo extraer const DATA")
    return json.loads(match.group(1))


def run_browser_checks(rows: list[dict]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        for row in rows:
            row["browser"] = f"omitido: Playwright no disponible ({exc})"
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for row in rows:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            errors = []
            page.on("pageerror", lambda exc, errors=errors: errors.append(str(exc)))
            page.goto((BASE / f"{row['tema']}_tbip_nominate.html").as_uri(), wait_until="load")
            page.wait_for_timeout(900)
            rendered = page.evaluate(
                """
                () => {
                  const svg = document.querySelector("#visualizer-chart");
                  return {
                    circles: svg ? svg.querySelectorAll("circle").length : -1,
                    lines: svg ? svg.querySelectorAll("line").length : -1,
                    svgWidth: svg ? svg.clientWidth : 0,
                    svgHeight: svg ? svg.clientHeight : 0,
                    activeTab: document.querySelector(".visualizer-tabs-container .tab-btn.active")?.id || null
                  };
                }
                """
            )
            row["browser"] = rendered
            row["js_errors"] = errors
            assert not errors, f"{row['tema']}: errores JS: {errors[:3]}"
            assert rendered["svgWidth"] > 0 and rendered["svgHeight"] > 0, f"{row['tema']}: SVG sin dimensiones"
            assert rendered["circles"] > 0, f"{row['tema']}: SVG sin puntos renderizados"
            page.close()
        browser.close()


def main() -> int:
    rows = []
    for tema in THEMES:
        html_path = BASE / f"{tema}_tbip_nominate.html"
        assert html_path.exists(), f"{tema}: HTML no existe"
        text = html_path.read_text(encoding="utf-8")
        for marker in REQUIRED:
            assert marker in text, f"{tema}: falta marcador {marker}"
        assert "footer-gen-date" in text, f"{tema}: falta nodo de compatibilidad footer-gen-date"
        assert "visualizer-render-recovery" in text, f"{tema}: falta script de recuperación de render"
        assert "D:/CEP" not in text, f"{tema}: contiene ruta absoluta D:/CEP"
        assert "NaN" not in text, f"{tema}: contiene NaN"
        assert "[object Object]" not in text, f"{tema}: contiene [object Object]"

        data = parse_data(text)
        row = {
            "tema": tema,
            "html_existe": "sí",
            "const_data": "sí",
            "members": len(data.get("members", [])),
            "matched": len(data.get("matched", [])),
            "nominate_all": len(data.get("nominate_all", [])),
            "topics": len(data.get("topics", [])),
            "ids": "sí",
            "estado": "OK",
        }
        assert row["members"] > 0, f"{tema}: DATA.members vacío"
        assert row["matched"] > 0, f"{tema}: DATA.matched vacío"
        assert row["nominate_all"] > 0, f"{tema}: DATA.nominate_all vacío"
        rows.append(row)

    run_browser_checks(rows)

    lines = [
        "# Auditoría funcional de visualizadores temáticos",
        "",
        "| tema | HTML existe | const DATA | members n | matched n | nominate_all n | topics n | ids del visualizador | render navegador | estado final |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        browser = row.get("browser", {})
        if isinstance(browser, dict):
            render = f"{browser.get('circles', 0)} puntos; {browser.get('svgWidth', 0)}x{browser.get('svgHeight', 0)}"
        else:
            render = str(browser)
        lines.append(
            f"| {row['tema']} | {row['html_existe']} | {row['const_data']} | {row['members']} | "
            f"{row['matched']} | {row['nominate_all']} | {row['topics']} | {row['ids']} | {render} | {row['estado']} |"
        )
    (BASE / "audit_visualizadores_datos.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Smoke test visualizadores OK")
    print(str(BASE / "audit_visualizadores_datos.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
