#------------------------------- educacion_basica

import pandas as pd
import numpy as np
import boto3
from io import BytesIO

def main():
    bucket_bronze = 'tfm-educ-app-bronze'
    bucket_silver = 'tfm-educ-app-silver'
    file_key = 'cobertura_municipios/MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR__B_SICA_Y_MEDIA_POR_MUNICIPIO_20250619.csv'
    output_key = 'cobertura_municipios/educacion_basica.csv'

    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_bronze, Key=file_key)

    try:
        df = pd.read_csv(obj['Body'], encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(obj['Body'], encoding='latin1')

    df = df[df['AÑO'] >= 2011]

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.replace(' ', '_')
        .str.replace('__', '_')
        .str.replace(r'[^\w]', '', regex=True)
    )

    df.replace('-', np.nan, inplace=True)

    columnas_entero = ['ano', 'codigo_departamento', 'codigo_municipio', 'codigo_etc', 'poblacion_5_16']
    columnas_texto = ['municipio', 'departamento', 'etc']
    columnas_numericas = df.columns.difference(columnas_entero + columnas_texto)

    # Convertir columnas enteras solo si no son NaN
    for col in columnas_entero:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').round().astype('Int64')

    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'nan': None, 'NaN': None})

    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)

    s3.put_object(Bucket=bucket_silver, Key=output_key, Body=buffer.getvalue())

def lambda_handler(event, context):
    main()
    return {
        'statusCode': 200,
        'body': 'Archivo procesado y guardado correctamente en el bucket silver.'
    }
