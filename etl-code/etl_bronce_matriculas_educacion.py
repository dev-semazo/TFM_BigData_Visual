#------------------ Matricula educación

import boto3
import pandas as pd
from io import BytesIO
import gc
import unicodedata

s3_client = boto3.client('s3')
bucket_origen = 'tfm-educ-app-bronze'
bucket_destino = 'tfm-educ-app-silver'

def normalizar_columna(col):
    col = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8')
    return col.strip().lower().replace(" ", "_")

def lambda_handler(event, context):
    try:
        print("Iniciando procesamiento de archivo de matrículas...")

        key_origen = 'matriculas_educacion/MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20250619.csv'
        response = s3_client.get_object(Bucket=bucket_origen, Key=key_origen)
        df = pd.read_csv(BytesIO(response['Body'].read()), encoding='utf-8')

        print("Archivo leído correctamente desde bucket bronze.")

        max_anio = df['AÑO'].max()
        df = df[df['AÑO'] >= max_anio - 9]

        df.columns = [normalizar_columna(c) for c in df.columns]

        df.rename(columns={
            'codigo_deldepartamento': 'codigo_del_departamento',
            'codigo_delmunicipio': 'codigo_del_municipio'
        }, inplace=True)

        columnas_enteras = [
            'ano', 'codigo_del_departamento', 'codigo_del_municipio',
            'tecnica_pro', 'tecnologica', 'universitaria',
            'especializacion', 'maestria', 'doctorado', 'ies_con_oferta'
        ]

        columnas_texto = ['nombre_del_departamento', 'nombre_del_municipio']

        for col in columnas_enteras:
            if col in df.columns:
                df[col] = df[col].replace('-', pd.NA)
                df[col] = pd.to_numeric(df[col], errors='coerce').round().astype('Int64')

        for col in columnas_texto:
            if col in df.columns:
                df[col] = df[col].replace('-', '').astype(str).fillna('')

        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)

        key_destino = 'matriculas_educacion/matriculas_limpio.csv'

        print(f"Guardando en s3://{bucket_destino}/{key_destino}...")
        s3_client.put_object(
            Bucket=bucket_destino,
            Key=key_destino,
            Body=buffer.getvalue()
        )

        print(" Archivo guardado exitosamente en bucket silver.")
        print(f"Total de filas procesadas: {df.shape[0]}")

        del df
        gc.collect()

        return {
            'statusCode': 200,
            'body': 'Archivo de matrículas limpio guardado exitosamente.'
        }

    except Exception as e:
        print(f" Error durante la ejecución: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error procesando archivo de matrículas: {str(e)}"
        }

