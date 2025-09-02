#####----------------------------------------------- Establecimientos educativos

import pandas as pd
import numpy as np
import boto3
from io import BytesIO

def lambda_handler(event, context):
    # Parámetros de entrada y salida en S3
    bucket_origen = 'tfm-educ-app-bronze'
    bucket_destino = 'tfm-educ-app-silver'
    file_key = 'establecimientos_educativos/MEN_ESTABLECIMIENTOS_EDUCATIVOS_PREESCOLAR_B_SICA_Y_MEDIA_20250619.csv'
    output_key = 'establecimientos_educativos/establecimientos_limpio.csv'

    # Cliente S3
    s3 = boto3.client('s3')
    
    # Leer el archivo desde S3
    response = s3.get_object(Bucket=bucket_origen, Key=file_key)
    df = pd.read_csv(response['Body'], encoding='latin1')

    # Eliminar columnas innecesarias
    columnas_a_eliminar = ['WEB', 'FAX', 'EMAIL', 'COD_CARACTER', 'CARACTER', 'TELEFONO', 'BARRIO_VEREDA', 'COD_SECTOR', 'SECTOR',	'COD_CARACTER', 'CARACTER' , 'COD_CALENDARIO', 'RECTOR'
]
    df.drop(columns=columnas_a_eliminar, inplace=True, errors='ignore')

    # Reemplazar '-' por NaN
    df.replace('-', np.nan, inplace=True)

    # Limpiar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('__', '_')
    )

    # Convertir columnas al tipo adecuado
    df = df.convert_dtypes()

    # Exportar el archivo limpio a un buffer
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)

    # Guardar en el bucket destino
    s3.put_object(Bucket=bucket_destino, Key=output_key, Body=buffer.getvalue())

    return {
        'statusCode': 200,
        'body': f'Archivo limpio cargado correctamente en {bucket_destino}/{output_key}'
    }

