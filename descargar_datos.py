"""
Descarga los datos abiertos reales necesarios para el dashboard:

  1. Indicadores CONEVAL 2020 a nivel municipal por grupo poblacional.
     Es la medicion mas reciente disponible (la metodologia oficial se
     publica cada 5 anos para nivel municipal).
     Incluye 7 grupos: indigena, ambito rural/urbano, edades, sexo.

  2. GeoJSON con los limites geograficos de los 212 municipios de
     Veracruz (CONABIO 2023, via repositorio publico).

Ambos archivos son datos publicos, sin autenticacion ni API key.
"""

import urllib.request
import os
import sys

FUENTES = [
    {
        "nombre": "CONEVAL 2020 — Pobreza municipal por grupo poblacional",
        "url":    "https://www.coneval.org.mx/Informes/Pobreza/Datos_abiertos/pobreza_municipal/grupos_pobla/grupos_poblacionales_2020.csv",
        "destino": "coneval_2020_raw.csv",
        "descripcion": (
            "Dataset oficial de CONEVAL 2020 a nivel municipal con 8 indicadores "
            "(pobreza, plp, ic_rezedu, ic_asalud, ic_segsoc, ic_cv, ic_sbv, ic_ali) "
            "desglosados por 9 grupos poblacionales (rural, urbano, hombres, mujeres, "
            "indigena, niños, jovenes, adultos, adultos mayores). "
            "~170,000 filas en formato long, 18.6 MB."
        ),
    },
    {
        "nombre": "GeoJSON de municipios de Veracruz",
        "url":    "https://raw.githubusercontent.com/PhantomInsights/mexico-geojson/main/2023/states/Veracruz%20de%20Ignacio%20de%20la%20Llave.json",
        "destino": "veracruz_geo.json",
        "descripcion": "Limites geograficos de los 212 municipios de Veracruz (CONABIO 2023).",
    },
]


def descargar(url, destino):
    headers = {"User-Agent": "portafolio-veracruz/1.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp, open(destino, "wb") as f:
        f.write(resp.read())
    return os.path.getsize(destino)


def main():
    print("=" * 70)
    print("  DESCARGA DE DATOS ABIERTOS — VERACRUZ 2020")
    print("=" * 70)
    print()

    for fuente in FUENTES:
        print(f"[*] {fuente['nombre']}")
        print(f"    URL: {fuente['url']}")
        if os.path.exists(fuente["destino"]):
            size_existente = os.path.getsize(fuente["destino"])
            print(f"    [OK] Ya existe ({size_existente:,} bytes), se reutiliza.")
        else:
            try:
                size = descargar(fuente["url"], fuente["destino"])
                print(f"    [OK] Descargado: {fuente['destino']} ({size:,} bytes)")
            except Exception as e:
                print(f"    [ERROR] {e}")
                sys.exit(1)
        print(f"    {fuente['descripcion']}")
        print()

    print("=" * 70)
    print("  Siguiente paso:  python preparar_datos.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
