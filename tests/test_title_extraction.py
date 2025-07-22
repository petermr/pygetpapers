#!/usr/bin/env python3
"""
Test script to debug title extraction logic.
"""

import re


def test_title_extraction():
    """Test the title extraction logic with the actual content."""

    # This is the text content we saw in the debug output
    text_content = """@charset "UTF-8";[ng\:cloak],[ng-cloak],[data-ng-cloak],[x-ng-cloak],.ng-cloak,.x-ng-cloak,.ng-hide:not(.ng-hide-animate){display:none !important;}ng\:form{display:block;}.ng-animate-shim{visibility:hidden;}.ng-anchor{position:absolute;} NOVEDADES NOMENCLATURALES EN LOS GÉNEROS LIPPIA Y LANTANA (VERBENACEAE) var _gaq = _gaq || []; _gaq.push([ '_setAccount', 'UA-3153272-1' ]); _gaq.push([ '_trackPageview' ]); (function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true; ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s); })(); window.dataLayer = window.dataLayer || []; function gtag() { dataLayer.push(arguments); } gtag('js', new Date()); gtag('config', 'G-PG5DW8YGFY'); /** evento de visita */ gtag('event', 'screen_view', { 'app_name' : 'PortalRedalyc', 'screen_name' : 'HomeArticulo' }); gtag('event', 'page_view', { 'page_title' : 'Articulo', 'page_location' : 'https://redalyc.org/articulo.oa' }); Sistema de Información Científica Redalyc Red de revistas científicas de Acceso Abierto diamante Infraestructura abierta no comercial propiedad de la academia esp eng NOVEDADES NOMENCLATURALES EN LOS GÉNEROS LIPPIA Y LANTANA (VERBENACEAE) Alicia D. Rotman, María E. Múlgura de Romero Darwiniana&nbsp;2010, &nbsp;48&nbsp;(1) PDF ¿Cómo citar? Exportar cita Número completo Indicadores Sistema de Información Científica Redalyc ® Red de revistas científicas de Acceso Abierto no comercial propiedad de la academia. Redalyc Versión 5.0 | 2003-2025 comunicacion@redalyc.org document.addEventListener("DOMContentLoaded", function() { // Obtiene el año actual const currentYear = new Date().getFullYear(); // Establece el contenido del span con id 'current-year' const yearSpan = document.getElementById('current-year'); if (yearSpan) { yearSpan.textContent = currentYear; } });"""

    print("Testing title extraction logic...")
    print(f"Text content length: {len(text_content)}")

    # Try the new approach
    text_parts = re.split(r"[;,]", text_content)
    print(f"Split into {len(text_parts)} parts")

    best_title = ""
    for i, part in enumerate(text_parts):
        part = part.strip()
        print(f"\nPart {i+1}: '{part[:100]}...'")

        # Check conditions
        length_ok = len(part) > 20
        keywords_ok = any(
            keyword in part.upper()
            for keyword in ["LIPPIA", "LANTANA", "VERBENACEAE", "NOMENCLATURALES"]
        )
        not_redalyc = "redalyc" not in part.lower()
        not_sistema = "sistema" not in part.lower()
        not_info = "información" not in part.lower()
        not_cientifica = "científica" not in part.lower()
        longer = len(part) > len(best_title)

        print(f"  Length > 20: {length_ok}")
        print(f"  Has keywords: {keywords_ok}")
        print(f"  Not redalyc: {not_redalyc}")
        print(f"  Not sistema: {not_sistema}")
        print(f"  Not info: {not_info}")
        print(f"  Not cientifica: {not_cientifica}")
        print(f"  Longer than current: {longer}")

        if (
            length_ok
            and keywords_ok
            and not_redalyc
            and not_sistema
            and not_info
            and not_cientifica
            and longer
        ):
            best_title = part
            print(f"  -> NEW BEST TITLE: '{best_title}'")

    print(f"\nFinal best title: '{best_title}'")


if __name__ == "__main__":
    test_title_extraction()
