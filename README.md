# Pobreza, Salud y Educación en Veracruz

Dashboard interactivo que estudia los 212 municipios de Veracruz a partir de los indicadores oficiales de **CONEVAL 2020** (la medición municipal más reciente publicada por el Consejo Nacional de Evaluación de la Política de Desarrollo Social). Incluye mapa coroplético, comparativa contra el promedio nacional, ranking municipal, correlación entre pobreza/educación/salud, y **desglose por grupo demográfico** (sexo, ámbito rural-urbano, edades, población indígena).

## Problema que resuelve

Veracruz es uno de los estados con mayor población del país (8.16 millones de habitantes) y al mismo tiempo uno con los indicadores socioeconómicos más críticos. Las decisiones de política pública, inversión social, expansión de programas educativos o de salud requieren saber **qué municipios están peor, qué carencias son las más comunes, cómo se compara la situación local contra el promedio nacional, y qué grupos demográficos están más afectados**. Este dashboard hace ese análisis con un solo clic.

## Características

- **Mapa coroplético** de los 212 municipios coloreados según el indicador seleccionado
- **Selector dinámico** entre 8 indicadores CONEVAL 2020 (pobreza, línea de pobreza por ingresos, rezago educativo, acceso a salud, seguridad social, vivienda, servicios básicos, alimentación)
- **Comparativa Veracruz vs Nacional** — barras divergentes con la brecha en puntos porcentuales para cada indicador
- **KPIs ejecutivos**: población analizada, % pobreza estatal, % bajo línea de pobreza, indicador activo — todos con delta vs el promedio nacional
- **Ranking municipal** — Top N peores y Top N mejores municipios para el indicador seleccionado
- **Histograma de distribución** con líneas de referencia (mediana estatal, promedio nacional)
- **Scatter de correlación tripartita** — pobreza × rezago educativo × acceso a salud × población, con coeficientes de Pearson
- **Desglose por grupo demográfico** (nuevo en CONEVAL 2020): cómo cada indicador afecta distinto a hombres vs mujeres, rural vs urbano, niñez/jóvenes/adultos/mayores y población indígena
- **Filtro por tamaño de municipio** para enfocar en localidades grandes o pequeñas
- **Tabla detallada exportable** a CSV

## Fuentes de datos (100% reales, 100% abiertas, datos 2020)

### 1. CONEVAL — Indicadores municipales 2020 por grupo poblacional
CSV oficial de CONEVAL descargado **directo del sitio del Consejo** ([coneval.org.mx](https://www.coneval.org.mx)):
- URL: `https://www.coneval.org.mx/Informes/Pobreza/Datos_abiertos/pobreza_municipal/grupos_pobla/grupos_poblacionales_2020.csv`
- 170,520 filas en formato long
- 18.6 MB
- 8 indicadores × 9 grupos poblacionales × 2,457 municipios del país
- **Encoding UTF-8 con BOM, con código `-999` para datos no disponibles** (el script los filtra automáticamente)

### 2. CONABIO — Geometrías municipales 2023
GeoJSON con los polígonos de los 212 municipios de Veracruz (descargado de [PhantomInsights/mexico-geojson](https://github.com/PhantomInsights/mexico-geojson), mirror de los shapefiles oficiales de CONABIO).

## Tecnologías

- Python 3.10+
- Streamlit
- Pandas
- Plotly (incluyendo `choropleth_mapbox` para el mapa)
- NumPy

## Instalación

```bash
git clone https://github.com/israel44moran/dashboard-veracruz.git
cd dashboard-veracruz
pip install -r requirements.txt
```

## Uso

```bash
# 1. Descarga los datos abiertos (CONEVAL 2020 + GeoJSON CONABIO)
python descargar_datos.py

# 2. Procesa el formato long, deriva el total municipal y valida el join
python preparar_datos.py

# 3. Lanza el dashboard
streamlit run dashboard.py
```

Disponible en `http://localhost:8501`

## Estructura del proyecto

```
dashboard-veracruz/
├── descargar_datos.py        # Baja CSV CONEVAL 2020 + GeoJSON Veracruz
├── preparar_datos.py         # Procesa formato long, deriva totales,
│                             #   genera dos vistas (wide + por grupos)
├── dashboard.py              # Aplicacion Streamlit (mapa + 6 graficos)
├── coneval_2020_raw.csv      # CSV crudo descargado (18.6 MB, 170k filas)
├── veracruz_geo.json         # GeoJSON descargado (212 features)
├── veracruz_municipios.csv   # Wide table (generado): 212 mun x 8 indicadores
├── veracruz_grupos.csv       # Long table (generado): por grupo demografico
├── metadata.json             # Promedios estatales y nacionales (generado)
├── requirements.txt
└── README.md
```

## Indicadores incluidos

| Código | Nombre | Categoría |
|---|---|---|
| `pobreza` | Pobreza multidimensional | Pobreza |
| `plp` | Por línea de pobreza (ingreso) | Pobreza |
| `ic_rezedu` | Rezago educativo | **Educación** |
| `ic_asalud` | Sin acceso a servicios de salud | **Salud** |
| `ic_segsoc` | Sin acceso a seguridad social | Salud |
| `ic_cv` | Vivienda de mala calidad | Vivienda |
| `ic_sbv` | Sin servicios básicos en vivienda | Vivienda |
| `ic_ali` | Sin acceso a la alimentación | Alimentación |

## Grupos demográficos disponibles (corte 2020)

| Grupo | Categoría |
|---|---|
| Hombres / Mujeres | Sexo |
| Rural / Urbano | Ámbito de residencia |
| Niñez (0-17) / Jóvenes (18-29) / Adultos (30-64) / Adultos mayores (65+) | Edad |
| Población indígena | Hablante |

## Hallazgos destacados (datos reales 2020)

Con todos los municipios y los indicadores ponderados por población:

| Indicador | Veracruz | Nacional | Brecha |
|---|---:|---:|---:|
| Pobreza multidimensional | 61.1% | 44.5% | **+16.7 pp** |
| Línea de pobreza por ingreso | 66.7% | 52.2% | +14.5 pp |
| Rezago educativo | 25.7% | 16.3% | **+9.4 pp** |
| Sin acceso a salud | 31.0% | 28.3% | +2.6 pp |
| Sin seguridad social | 67.9% | 56.7% | +11.2 pp |
| Vivienda mala calidad | 15.0% | 9.4% | +5.6 pp |
| Sin servicios básicos | 37.4% | 27.6% | +9.8 pp |
| Sin acceso a alimentación | 22.9% | 20.9% | +2.0 pp |

**Veracruz está peor que el promedio nacional en TODOS los indicadores**, con brechas especialmente grandes en pobreza multidimensional, rezago educativo y servicios básicos en vivienda.

## Sobre el origen del proyecto

El plan original del portafolio mencionaba "Dashboard en Power BI sobre salud o educación en Veracruz". Se construyó en Streamlit/Plotly por flexibilidad técnica, pero el dataset utilizado (CONEVAL 2020) cubre simultáneamente los temas de pobreza, **salud** (carencia de servicios médicos) y **educación** (rezago educativo) — y agrega el bonus de los **cortes demográficos** que en una primera versión con datos 2015 no estaban disponibles. La misma lógica puede replicarse en Power BI Desktop usando los archivos `veracruz_municipios.csv`, `veracruz_grupos.csv` y `veracruz_geo.json` como fuentes.

## Autor

Israel Morán
