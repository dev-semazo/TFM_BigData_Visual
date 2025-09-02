#######--------------  Nacimientos 2023-2019

import pandas as pd
import boto3
import io
import re
from datetime import datetime

def es_texto_util(x):
    if x is None:
        return False
    s = str(x).strip()
    return s != "" and s.lower() != "nan"

# Mapa DANE: 2 dígitos -> nombre del departamento
MAPA_DEPTOS = {
    "05": "Antioquia",
    "08": "Atlántico",
    "11": "Bogotá, D.C.",
    "13": "Bolívar",
    "15": "Boyacá",
    "17": "Caldas",
    "18": "Caquetá",
    "19": "Cauca",
    "20": "Cesar",
    "23": "Córdoba",
    "25": "Cundinamarca",
    "27": "Chocó",
    "41": "Huila",
    "44": "La Guajira",
    "47": "Magdalena",
    "50": "Meta",
    "52": "Nariño",
    "54": "Norte de Santander",
    "63": "Quindío",
    "66": "Risaralda",
    "68": "Santander",
    "70": "Sucre",
    "73": "Tolima",
    "76": "Valle del Cauca",
    "81": "Arauca",
    "85": "Casanare",
    "86": "Putumayo",
    "88": "San Andrés y Providencia",
    "91": "Amazonas",
    "94": "Guainía",
    "95": "Guaviare",
    "97": "Vaupés",
    "99": "Vichada",
}

def lambda_handler(event, context):
    bucket_input  = "tfm-educ-app-bronze"
    key_input     = "nacimientos_colombia/anex-EEVV-Nacimientos2023pCuadroDefinivo-2023.xlsx"

    bucket_output = "tfm-educ-app-silver"
    fecha         = datetime.now().strftime("%Y%m%d")

    #  Detectar automáticamente el año desde el nombre del archivo
    m = re.search(r"(20\d{2})", key_input)
    anio_archivo = int(m.group(1)) if m else datetime.now().year

    # Opcional: incluir el año detectado en el nombre del CSV de salida
    key_output    = f"nacimientos_colombia_limpio/nacimientos_colombia_{anio_archivo}_{fecha}.csv"

    s3 = boto3.client("s3")

    try:
        # Leer Excel
        obj = s3.get_object(Bucket=bucket_input, Key=key_input)
        xls = io.BytesIO(obj["Body"].read())

        df_raw = pd.read_excel(xls, sheet_name="Cuadro2", header=0, skiprows=7)
        df_raw = df_raw.dropna(axis=1, how="all").copy()

        # Buscar etiquetas en primeras columnas
        primeras_cols = df_raw.columns[:6].tolist()
        patron_muni = re.compile(r"^\s*\d{5}\s")  # "05001 Medellín"

        depto_actual = None
        filas, dptos, munis = [], [], []

        for _, row in df_raw.iterrows():
            textos = []
            for c in primeras_cols:
                val = row.get(c, None)
                if es_texto_util(val):
                    textos.append(str(val).strip())

            if not textos:
                continue

            if any("Total Nacional" in t for t in textos):
                continue

            t_dpto = next((t for t in textos if "Total Dpto" in t), None)
            if t_dpto is not None:
                depto_actual = t_dpto.replace("Total Dpto", "").strip()
                continue

            t_muni = next((t for t in textos if patron_muni.match(t)), None)
            if t_muni is None:
                continue

            filas.append(row.to_dict())
            dptos.append(depto_actual)
            munis.append(t_muni)

        if not filas:
            raise ValueError("No se encontraron municipios. Verifica que la hoja sea 'Cuadro2' y que el patrón '##### Nombre' esté en las primeras columnas.")

        dfm = pd.DataFrame(filas)
        dfm["Departamento"] = dptos
        dfm["Municipio"]    = munis

        # Detectar bloque de métricas desde la primera columna llamada 'Total'
        cols = list(dfm.columns)
        cand_idx = [i for i, c in enumerate(cols) if str(c).strip().lower() == "total"]
        if not cand_idx:
            raise ValueError(f"No se encontró la columna 'Total'. Columnas: {cols}")
        start = cand_idx[0]

        metric_src = cols[start:start+16]
        if len(metric_src) < 16:
            raise ValueError(f"Desde 'Total' solo hay {len(metric_src)} columnas. Detectadas: {metric_src}")

        metric_dst = [
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
        rename_map = {src: dst for src, dst in zip(metric_src, metric_dst)}
        dfm = dfm.rename(columns=rename_map)

        # Armar DataFrame final
        out_cols = ["Departamento", "Municipio"] + metric_dst
        df_final = dfm[out_cols].copy()

        # Rellenar Departamento por prefijo del código de municipio si viene vacío
        def completar_depto(row):
            depto = str(row["Departamento"]).strip() if es_texto_util(row["Departamento"]) else ""
            muni  = str(row["Municipio"])
            m = re.match(r"^\s*(\d{2})\d{3}\s", muni)
            if m:
                pref = m.group(1)
                nombre = MAPA_DEPTOS.get(pref)
                if not depto and nombre:
                    return nombre
            return depto if depto else None

        df_final["Departamento"] = df_final.apply(completar_depto, axis=1)

        # Añadir columna Año (automática) y reordenar para que quede después de Municipio
        df_final["Año"] = anio_archivo
        df_final = df_final[["Departamento", "Municipio", "Año"] + metric_dst]

        # Métricas como enteros
        for col in metric_dst:
            df_final[col] = pd.to_numeric(df_final[col], errors="coerce").fillna(0).astype(int)

        # Exportar CSV con punto y coma y UTF-8 con BOM (Excel + Power BI OK)
        buf = io.StringIO()
        df_final.to_csv(buf, index=False, sep=";", encoding="utf-8-sig")
        s3.put_object(Bucket=bucket_output, Key=key_output, Body=buf.getvalue())

        return {"statusCode": 200, "body": f" Archivo limpio con Año={anio_archivo}: s3://{bucket_output}/{key_output}"}

    except Exception as e:
        return {"statusCode": 500, "body": f" Error en Lambda: {str(e)}"}


