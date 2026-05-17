"""
Procesa CONEVAL 2020 (formato long, por grupo poblacional) y produce:

  - veracruz_municipios.csv  → tabla wide del TOTAL municipal (212 filas)
                               Total derivado de Hombres + Mujeres ponderado.
  - veracruz_grupos.csv      → tabla long con todos los grupos para
                               analizar desglose demografico (sexo, ambito,
                               edad, indigena).
  - metadata.json            → promedios estatales y nacionales,
                               descripcion de indicadores.

El archivo de entrada (coneval_2020_raw.csv) viene en formato long con
una fila por (municipio, grupo, indicador) y encoding latin-1.
"""

import pandas as pd
import json
import sys
import os

# ============================================================
# CONFIGURACION
# ============================================================
ENTIDAD_OBJETIVO = "Veracruz"
ARCHIVO_ENTRADA = "coneval_2020_raw.csv"

INDICADORES_META = {
    "pobreza":   ("Pobreza total",            "Pobreza",     "% de poblacion en pobreza multidimensional"),
    "plp":       ("Por linea de pobreza",     "Pobreza",     "% con ingreso inferior a la linea de pobreza por ingresos"),
    "ic_rezedu": ("Rezago educativo",         "Educacion",   "% con carencia por rezago educativo"),
    "ic_asalud": ("Sin acceso a salud",       "Salud",       "% con carencia por acceso a servicios de salud"),
    "ic_segsoc": ("Sin seguridad social",     "Salud",       "% con carencia por acceso a seguridad social"),
    "ic_cv":     ("Vivienda mala calidad",    "Vivienda",    "% con carencia por calidad y espacios de la vivienda"),
    "ic_sbv":    ("Sin servicios basicos",    "Vivienda",    "% con carencia por servicios basicos en la vivienda"),
    "ic_ali":    ("Sin acceso a alimentacion","Alimentacion","% con carencia por acceso a la alimentacion"),
}

# Mapeo de grupos del CSV a nombres legibles + categoria
GRUPOS_META = {
    "Población por sexo: hombres":            ("Hombres",          "Sexo"),
    "Población por sexo: mujeres":            ("Mujeres",          "Sexo"),
    "Ámbito de residencia: rural":            ("Rural",            "Ambito"),
    "Ámbito de residencia: urbano":           ("Urbano",           "Ambito"),
    "Niñas, niños y adolescentes (0 a 17 años)":  ("Niñez (0-17)",  "Edad"),
    "Jóvenes (18 a 29 años)":                 ("Jovenes (18-29)",  "Edad"),
    "Adultos (30 a 64 años)":                 ("Adultos (30-64)",  "Edad"),
    "Adultos mayores (65 o más años)":        ("Adultos mayores 65+", "Edad"),
    "Población indígena":                     ("Indigena",         "Hablante"),
}


# ============================================================
# PIPELINE
# ============================================================
def main():
    if not os.path.exists(ARCHIVO_ENTRADA):
        print(f"[ERROR] No existe {ARCHIVO_ENTRADA}.")
        print("        Corre primero: python descargar_datos.py")
        sys.exit(1)

    print(f"[*] Cargando {ARCHIVO_ENTRADA} (encoding utf-8-sig)...")
    df = pd.read_csv(ARCHIVO_ENTRADA, encoding="utf-8-sig")
    df.columns = [c.strip().lower() for c in df.columns]
    print(f"    Filas: {len(df):,} | Columnas: {list(df.columns)}")

    # Tipos
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["pobtot"] = pd.to_numeric(df["pobtot"], errors="coerce")
    df = df.dropna(subset=["valor", "pobtot"])
    df = df[df["pobtot"] > 0]

    # Filtrar codigo "sin dato" de CONEVAL: -999 (precision = "Sin precision")
    n_antes = len(df)
    df = df[df["valor"] >= 0]
    df = df[df["valor"] <= 100]  # son porcentajes, max 100
    print(f"    Filas validas (sin -999): {len(df):,} de {n_antes:,}")

    # Padded clave municipal (5 digitos)
    df["cvegeo"] = df["cve_mun"].astype(int).astype(str).str.zfill(5)

    # ============================================================
    # PROMEDIOS NACIONALES — ponderados, derivados de Hombres+Mujeres
    # ============================================================
    print("[*] Calculando promedios nacionales (ponderado Hombres + Mujeres)...")
    sexo_mask = df["grupo"].isin([
        "Población por sexo: hombres",
        "Población por sexo: mujeres",
    ])
    nac = df[sexo_mask].copy()

    promedios_nacionales = {}
    for ind in INDICADORES_META:
        sub = nac[nac["indicador"] == ind]
        if len(sub) > 0:
            promedios_nacionales[ind] = round(
                (sub["valor"] * sub["pobtot"]).sum() / sub["pobtot"].sum(), 2
            )

    # ============================================================
    # FILTRAR VERACRUZ
    # ============================================================
    print(f"[*] Filtrando entidad: {ENTIDAD_OBJETIVO}")
    ver = df[df["ent"].str.contains(ENTIDAD_OBJETIVO, na=False)].copy()
    print(f"    Filas Veracruz: {len(ver):,}")
    print(f"    Municipios:     {ver['cvegeo'].nunique()}")

    # ============================================================
    # TABLA WIDE — TOTAL MUNICIPAL (Hombres + Mujeres)
    # ============================================================
    print("[*] Construyendo tabla TOTAL por municipio (Hombres+Mujeres ponderado)...")
    sexo_ver = ver[ver["grupo"].isin([
        "Población por sexo: hombres",
        "Población por sexo: mujeres",
    ])].copy()

    # Promedio ponderado por (cvegeo, mun, indicador) via vectorizado
    sexo_ver["_num"] = sexo_ver["valor"] * sexo_ver["pobtot"]
    agg = (
        sexo_ver.groupby(["cvegeo", "mun", "indicador"], as_index=False)
                .agg(_num=("_num", "sum"), _den=("pobtot", "sum"))
    )
    agg["valor"] = agg["_num"] / agg["_den"]
    total = agg[["cvegeo", "mun", "indicador", "valor"]]

    # Poblacion total = suma de hombres + mujeres
    poblacion_mun = (
        sexo_ver.groupby(["cvegeo"])["pobtot"].sum().reset_index()
                .rename(columns={"pobtot": "poblacion"})
    )
    # Como cada municipio aparece una vez por (sexo x indicador),
    # la suma anterior cuenta hombres+mujeres por cada indicador.
    # Hay que dividir entre el numero de indicadores para no duplicar.
    n_indicadores = sexo_ver["indicador"].nunique()
    poblacion_mun["poblacion"] = (poblacion_mun["poblacion"] / n_indicadores).round().astype(int)

    # Pivot a wide
    wide = total.pivot(index=["cvegeo", "mun"], columns="indicador", values="valor").reset_index()
    wide.columns.name = None
    wide = wide.merge(poblacion_mun, on="cvegeo", how="left")

    # Limpieza nombre municipio
    wide["municipio"] = wide["mun"].astype(str)
    wide = wide.drop(columns=["mun"])

    # Orden de columnas
    cols = ["cvegeo", "municipio", "poblacion"] + list(INDICADORES_META.keys())
    cols = [c for c in cols if c in wide.columns]
    wide = wide[cols].sort_values("municipio").reset_index(drop=True)

    wide.to_csv("veracruz_municipios.csv", index=False, encoding="utf-8")
    print(f"    [OK] veracruz_municipios.csv ({len(wide)} municipios)")

    # ============================================================
    # TABLA LONG — DESGLOSE POR GRUPO (rural/urbano, edad, indigena, sexo)
    # ============================================================
    print("[*] Construyendo tabla por GRUPO POBLACIONAL...")
    ver["grupo_corto"] = ver["grupo"].map(lambda g: GRUPOS_META.get(g, (g, "Otro"))[0])
    ver["grupo_categoria"] = ver["grupo"].map(lambda g: GRUPOS_META.get(g, (g, "Otro"))[1])

    grupos = ver[["cvegeo", "mun", "grupo_corto", "grupo_categoria",
                  "indicador", "valor", "pobtot"]].copy()
    grupos.columns = ["cvegeo", "municipio", "grupo", "categoria_grupo",
                      "indicador", "valor", "poblacion_grupo"]
    grupos.to_csv("veracruz_grupos.csv", index=False, encoding="utf-8")
    print(f"    [OK] veracruz_grupos.csv ({len(grupos):,} filas)")

    # ============================================================
    # METADATA
    # ============================================================
    poblacion_total = int(wide["poblacion"].sum())

    # Promedios estatales (ponderados por poblacion municipal)
    promedios_estado = {}
    for ind in INDICADORES_META:
        if ind in wide.columns:
            promedios_estado[ind] = round(
                (wide[ind] * wide["poblacion"]).sum() / wide["poblacion"].sum(), 2
            )

    metadata = {
        "fuente":              "CONEVAL 2020 — Pobreza municipal por grupo poblacional",
        "url_fuente":          "https://www.coneval.org.mx/Informes/Pobreza/Datos_abiertos/pobreza_municipal/grupos_pobla/grupos_poblacionales_2020.csv",
        "anio":                2020,
        "n_municipios":        int(len(wide)),
        "poblacion_total":     poblacion_total,
        "promedios_estado":    promedios_estado,
        "promedios_nacionales": promedios_nacionales,
        "indicadores_metadata": {
            k: {"nombre": v[0], "categoria": v[1], "descripcion": v[2]}
            for k, v in INDICADORES_META.items()
        },
        "grupos_metadata": {
            v[0]: v[1] for v in GRUPOS_META.values()
        },
    }
    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"    [OK] metadata.json")

    # ============================================================
    # VALIDACION JOIN
    # ============================================================
    if os.path.exists("veracruz_geo.json"):
        with open("veracruz_geo.json", encoding="utf-8") as f:
            geo = json.load(f)
        ids_geo = {feat["properties"]["CVEGEO"] for feat in geo["features"]}
        ids_csv = set(wide["cvegeo"])
        match = len(ids_geo & ids_csv)
        print(f"    [OK] Join CSV-GeoJSON: {match}/{len(ids_csv)} coinciden")

    # ============================================================
    # RESUMEN
    # ============================================================
    print()
    print("=" * 70)
    print(f"  RESUMEN VERACRUZ 2020 ({len(wide)} municipios, {poblacion_total:,} habitantes)")
    print("=" * 70)
    print(f"{'Indicador':<32} {'Veracruz':>10} {'Nacional':>10} {'Brecha':>10}")
    print("-" * 64)
    for ind, info in INDICADORES_META.items():
        if ind in promedios_estado and ind in promedios_nacionales:
            v = promedios_estado[ind]
            n = promedios_nacionales[ind]
            d = round(v - n, 1)
            arrow = "(+)" if d > 0 else "(-)"
            print(f"  {info[0]:<30} {v:>9}% {n:>9}% {arrow:>5} {abs(d):>5}pp")

    print()
    print("  Siguiente paso:  streamlit run dashboard.py")


if __name__ == "__main__":
    main()
