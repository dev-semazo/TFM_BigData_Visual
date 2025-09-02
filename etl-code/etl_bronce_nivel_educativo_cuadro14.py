
#######------------------------ Nivel educativo edad Cuadro 14
import pandas as pd
import boto3
import io

def lambda_handler(event, context):
    bucket_bronze = 'tfm-educ-app-bronze'
    bucket_silver = 'tfm-educ-app-silver'
    
    file_key = 'nivel_educativo_edad/anex-ECV-Series-2018-2024.xlsx'
    output_key = 'nivel_educativo_edad/cuadro_14_limpio.csv'

    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_bronze, Key=file_key)
    excel_data = obj['Body'].read()

    df_raw = pd.read_excel(io.BytesIO(excel_data), sheet_name='Cuadro 14', header=11)

    df_raw = df_raw[df_raw.iloc[:, 0].notna()]
    patrones_excluir = ['Fuente:', 'Notas:', 'Actualizado el']
    df_raw = df_raw[~df_raw.iloc[:, 0].astype(str).str.contains('|'.join(patrones_excluir), na=False)]
    df_raw = df_raw[~df_raw.iloc[:, 0].astype(str).str.contains("Total nacional", na=False)]

    años = [2018, 2019, 2020, 2021, 2022, 2023]
    tipos_de_atencion = [
        "Hogar comunitario de bienestar familiar",
        "Hogar infantil o jardín de bienestar familiar",
        "Centro de desarrollo infantil público",
        "Jardín o colegio oficial",
        "Jardín o colegio privado"
    ]

    data = []

    for año in años:
        offset = (año - 2018) * 10 + 2
        for i, tipo in enumerate(tipos_de_atencion):
            col_total = df_raw.columns[offset + i * 2]
            col_pct = df_raw.columns[offset + i * 2 + 1]

            for idx, row in df_raw.iterrows():
                region = str(row.iloc[0]).strip()
                total = row[col_total]
                pct = row[col_pct]

                # Porcentaje
                if isinstance(pct, str):
                    pct = pct.replace('.', '').replace(',', '.')
                try:
                    porcentaje = round(float(pct), 1)
                except:
                    porcentaje = None

                # Total como entero
                try:
                    total_str = str(total).replace('.', '').replace(',', '').strip()
                    total_int = int(float(total_str)) if total_str.isdigit() or total_str.replace('.', '', 1).isdigit() else None
                except:
                    total_int = None

                data.append({
                    'region': region,
                    'año': año,
                    'tipo_de_atencion': tipo,
                    'porcentaje': porcentaje,
                    'total': total_int
                })

    df_final = pd.DataFrame(data)

    csv_buffer = io.StringIO()
    df_final.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket_silver, Key=output_key, Body=csv_buffer.getvalue().encode('utf-8-sig'))

    return {
        'statusCode': 200,
        'body': f'Archivo limpio guardado en s3://{bucket_silver}/{output_key}'
    }

