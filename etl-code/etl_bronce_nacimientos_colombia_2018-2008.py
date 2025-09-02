##### final de nacimientos del 2018-2008
import io
import re
import unicodedata
import boto3
import pandas as pd
from datetime import datetime

# Config 
BUCKET_IN  = "tfm-educ-app-bronze"
KEY_IN     = "nacimientos_colombia/Cuadro2-NACIMIENTOS-2008.xlsx"   # <-- ajusta si cambia
BUCKET_OUT = "tfm-educ-app-silver"
PREFIX_OUT = "nacimientos_colombia_limpio/"
# -----------

METRIC_DST = [
    "Total General",
    "Total Hombres",
    "Total Mujeres",
    "Total Indeterminado",
    "Cabecera municipal Hombres",
    "Cabecera municipal Mujeres",
    "Cabecera municipal Indeterminado",
    "Centro poblado Hombres",
    "Centro poblado Mujeres",
    "Centro poblado Indeterminado",
    "Rural disperso Hombres",
    "Rural disperso Mujeres",
    "Rural disperso Indeterminado",
    "Sin información Hombres",
    "Sin información Mujeres",
    "Sin información Indeterminado",
]
FINAL_COLS = ["Departamento", "Municipio", "AÑO"] + METRIC_DST

MAPA_DEPTOS = {
    "05":"Antioquia","08":"Atlántico","11":"Bogotá, D.C.","13":"Bolívar","15":"Boyacá","17":"Caldas",
    "18":"Caquetá","19":"Cauca","20":"Cesar","23":"Córdoba","25":"Cundinamarca","27":"Chocó",
    "41":"Huila","44":"La Guajira","47":"Magdalena","50":"Meta","52":"Nariño","54":"Norte de Santander",
    "63":"Quindío","66":"Risaralda","68":"Santander","70":"Sucre","73":"Tolima","76":"Valle del Cauca",
    "81":"Arauca","85":"Casanare","86":"Putumayo","88":"San Andrés y Providencia","91":"Amazonas",
    "94":"Guainía","95":"Guaviare","97":"Vaupés","99":"Vichada",
}

#  utilidades
def es_texto_util(x):
    if x is None: return False
    s = str(x).strip()
    return s != "" and s.lower() != "nan"

def fix_mojibake(s: str) -> str:
    if s is None: return s
    rep = {"AÃ‘O":"AÑO","AÃ±o":"Año","INFORMACIÃ“N":"INFORMACIÓN","InformaciÃ³n":"Información"}
    for k,v in rep.items():
        s = str(s).replace(k,v)
    return s

def norm(s: str) -> str:
    if s is None: return ""
    s = fix_mojibake(str(s))
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s.lower().strip())
    return s

def detectar_anio_desde_key(key: str, fallback: int) -> int:
    m = re.search(r"(19|20)\d{2}", key)
    return int(m.group(0)) if m else fallback

def encontrar_header_row(df: pd.DataFrame) -> int:
    top = min(80, len(df))
    for i in range(top):
        fila = " | ".join(norm(v) for v in df.iloc[i].astype(str).tolist())
        if "municipio" in fila and "total" in fila:
            return i
    for i in range(top):
        fila = " | ".join(norm(v) for v in df.iloc[i].astype(str).tolist())
        if "municipio" in fila or "total" in fila:
            return i
    return 0

# lectura con doble encabezado preservado
def leer_hoja_preservando_grupos(xls: pd.ExcelFile, sheet: str):
    ws0 = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=str, engine="openpyxl")
    if ws0 is None or ws0.empty:
        return pd.DataFrame(), None
    # intentamos capturar A10 (fila 9) por si sirve de rótulo
    depto_arriba = ws0.iat[9,0] if ws0.shape[0] > 9 and ws0.shape[1] > 0 else None
    depto_arriba = fix_mojibake(depto_arriba).strip() if es_texto_util(depto_arriba) else None

    hdr = encontrar_header_row(ws0)
    df = pd.read_excel(xls, sheet_name=sheet, header=[hdr, hdr+1], dtype=str, engine="openpyxl")
    if not isinstance(df.columns, pd.MultiIndex):
        one = pd.read_excel(xls, sheet_name=sheet, header=hdr, dtype=str, engine="openpyxl")
        cols0, cols1 = [], []
        for c in one.columns:
            cols0.append("")
            cols1.append(str(c))
        df = one.copy()
        df.columns = pd.MultiIndex.from_arrays([cols0, cols1])

    # ffill a la izquierda el nivel superior (celdas combinadas)
    top = list(df.columns.get_level_values(0))
    sub = list(df.columns.get_level_values(1))
    top = [t if es_texto_util(t) else None for t in top]
    last = None
    for i, t in enumerate(top):
        if t is None:
            top[i] = last
        else:
            last = t
    top = [fix_mojibake(t) if t is not None else "" for t in top]
    sub = [fix_mojibake(s) if es_texto_util(s) else "" for s in sub]
    df.columns = pd.MultiIndex.from_arrays([top, sub])
    df = df.dropna(axis=1, how="all").dropna(how="all")

    # normalizaciones ligeras
    repl = {"Indeterminados":"Indeterminado","Indeterminadas":"Indeterminado",
            "Sin informacion":"Sin información"}
    new_cols0, new_cols1 = [], []
    for g,s in df.columns:
        g2 = repl.get(g, g)
        s2 = repl.get(s, s)
        new_cols0.append(g2); new_cols1.append(s2)
    df.columns = pd.MultiIndex.from_arrays([new_cols0, new_cols1])

    return df, depto_arriba

# mapeo exacto por (grupo, sub)
def find_col(cols_multi, group_kw: list, sub_kw: list):
    for col in cols_multi:
        g, s = col[0], col[1]
        ng, ns = norm(g), norm(s)
        if all(k in ng for k in group_kw) and all(k in ns for k in sub_kw):
            return col
    return None

def construir_metricas(dfm: pd.DataFrame) -> pd.DataFrame:
    cols = list(dfm.columns)
    nrows = len(dfm)
    rules = {
        "Total General":               (["total"],              []),
        "Total Hombres":               (["total"],              ["hombre"]),
        "Total Mujeres":               (["total"],              ["mujer"]),
        "Total Indeterminado":         (["total"],              ["indeter"]),
        "Cabecera municipal Hombres":  (["cabecera"],           ["hombre"]),
        "Cabecera municipal Mujeres":  (["cabecera"],           ["mujer"]),
        "Cabecera municipal Indeterminado": (["cabecera"],      ["indeter"]),
        "Centro poblado Hombres":      (["centro","poblado"],   ["hombre"]),
        "Centro poblado Mujeres":      (["centro","poblado"],   ["mujer"]),
        "Centro poblado Indeterminado":(["centro","poblado"],   ["indeter"]),
        "Rural disperso Hombres":      (["rural","disperso"],   ["hombre"]),
        "Rural disperso Mujeres":      (["rural","disperso"],   ["mujer"]),
        "Rural disperso Indeterminado":(["rural","disperso"],   ["indeter"]),
        "Sin información Hombres":     (["sin","información"],  ["hombre"]),
        "Sin información Mujeres":     (["sin","información"],  ["mujer"]),
        "Sin información Indeterminado":(["sin","información"], ["indeter"]),
    }
    data = {}
    for dst, (gkw, skw) in rules.items():
        col = find_col(cols, gkw, skw)
        if col is not None:
            data[dst] = pd.to_numeric(dfm[col], errors="coerce")
        else:
            data[dst] = pd.Series([0]*nrows, index=dfm.index)
    out = pd.DataFrame(data, index=dfm.index)
    for c in METRIC_DST:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)
    return out

#  helpers de nombre de departamento 
def resolver_nombre_departamento(sheet_name: str, depto_arriba: str) -> str:
    """
    Regla especial: si la hoja es '11' => 'Bogotá, D.C.' siempre.
    Si la hoja es un código DANE (05,08,...) usa el mapa.
    Si hay texto arriba (A10) úsalo; si no, queda el nombre de la hoja.
    """
    s = sheet_name.strip()
    if s == "11":
        return "Bogotá, D.C."
    if s.zfill(2) in MAPA_DEPTOS:
        return MAPA_DEPTOS[s.zfill(2)]
    if es_texto_util(depto_arriba):
        return depto_arriba
    return sheet_name

#  extracción de municipios con fallback "Total depto" 
def extraer_municipios(df: pd.DataFrame, depto_nombre: str) -> pd.DataFrame:
    # detectar columna de municipio
    muni_col = None
    for col in df.columns:
        g, s = col[0], col[1]
        if "municipio" in norm(g) or "municipio" in norm(s):
            muni_col = col
            break
    if muni_col is None:
        muni_col = df.columns[0]

    patron_muni = re.compile(r"^\s*\d{5}\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")

    keep_idx, munis = [], []
    for i, val in enumerate(df[muni_col]):
        if es_texto_util(val) and patron_muni.match(str(val)):
            keep_idx.append(i)
            munis.append(str(val).strip())

    if not keep_idx:
        # Fila de TOTAL del departamento
        fila_total_idx = None
        for i, val in enumerate(df[muni_col]):
            if es_texto_util(val) and "total" in norm(val):
                fila_total_idx = i
                break
        if fila_total_idx is not None:
            df_row = df.iloc[[fila_total_idx]].copy()
            metrics = construir_metricas(df_row)
            out = pd.concat([
                pd.DataFrame({"Departamento":[depto_nombre], "Municipio":[f"{depto_nombre} (Total)"]}),
                metrics.reset_index(drop=True)
            ], axis=1)
            return out
        return pd.DataFrame(columns=["Departamento","Municipio"]+METRIC_DST)

    # Con municipios normales
    df_rows = df.iloc[keep_idx].copy()
    metrics = construir_metricas(df_rows)
    out = pd.concat([
        pd.DataFrame({"Departamento":[depto_nombre]*len(df_rows), "Municipio":munis}, index=df_rows.index).reset_index(drop=True),
        metrics.reset_index(drop=True)
    ], axis=1)
    return out

# Handler
def lambda_handler(event, context):
    s3 = boto3.client("s3")
    anio_archivo = detectar_anio_desde_key(KEY_IN, 2014)

    obj = s3.get_object(Bucket=BUCKET_IN, Key=KEY_IN)
    content = obj["Body"].read()

    xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")

    partes = []
    for sheet in xls.sheet_names:
        # Omitir Total Nacional
        if sheet.strip() == "00":
            print(f"Hoja '{sheet}' omitida (Total Nacional)")
            continue
        try:
            df_sheet, depto_arriba = leer_hoja_preservando_grupos(xls, sheet)
            if df_sheet.empty:
                print(f"Hoja '{sheet}' vacía")
                continue

            # nombre final del departamento (regla especial para la hoja '11')
            depto_nombre = resolver_nombre_departamento(sheet, depto_arriba)

            df_parte = extraer_municipios(df_sheet, depto_nombre)
            if df_parte.empty:
                print(f"Hoja '{sheet}' sin municipios ni total detectados")
                continue
            partes.append(df_parte)
        except Exception as e:
            print(f" Hoja '{sheet}' omitida: {e}")

    if not partes:
        return {"statusCode": 500, "body": "No se extrajo información de ninguna hoja."}

    df_all = pd.concat(partes, ignore_index=True)
    df_all["AÑO"] = anio_archivo

    # Asegurar columnas y orden
    for c in FINAL_COLS:
        if c not in df_all.columns:
            df_all[c] = 0 if c in METRIC_DST else pd.NA
    df_all = df_all[FINAL_COLS].copy()

    fecha = datetime.now().strftime("%Y%m%d")
    key_out = f"{PREFIX_OUT}nacimientos_{anio_archivo}_{fecha}.csv"

    buf = io.StringIO()
    df_all.to_csv(buf, index=False, sep=";", encoding="utf-8-sig")
    s3.put_object(Bucket=BUCKET_OUT, Key=key_out, Body=buf.getvalue())

    return {"statusCode": 200, "body": f" Archivo limpio ({len(df_all)} filas): s3://{BUCKET_OUT}/{key_out}"}
