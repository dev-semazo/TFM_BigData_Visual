##----------------------Nivel educativo edad Cuadro 15

import pandas as pd
import boto3
import io

def lambda_handler(event, context):
    # Configuración de S3
    bucket_bronze = 'tfm-educ-app-bronze'
    bucket_silver = 'tfm-educ-app-silver'

    file_key = 'nivel_educativo_edad/anex-ECV-Series-2018-2024.xlsx'
    output_key = 'nivel_educativo_edad/cuadro_15_limpio.csv'

    # Cliente S3
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_bronze, Key=file_key)
    excel_data = obj['Body'].read()

    # Leer hoja Cuadro 15
    df_raw = pd.read_excel(io.BytesIO(excel_data), sheet_name='Cuadro 15', header=11)

    # Limpiar filas vacías y eliminar notas
    df_raw = df_raw[df_raw.iloc[:, 0].notna()]
    frases_excluir = ['Fuente:', 'Notas:', 'Actualizado el']
    df_raw = df_raw[~df_raw.iloc[:, 0].astype(str).str.contains('|'.join(frases_excluir), case=False)]
    df_raw.rename(columns={df_raw.columns[0]: 'region'}, inplace=True)

    # Años y grupos
    años = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    grupos = ['6 a 21', '6 a 10', '11 a 14', '15 a 16', '17 a 21']

    # Índices 
    column_indices = {
        2018: {
            '6 a 21': (1, 2, 3),
            '6 a 10': (4, 5, 6),
            '11 a 14': (7, 8, 9),
            '15 a 16': (10, 11, 12),
            '17 a 21': (13, 14, 15),
        },
        2019: {
            '6 a 21': (17, 18, 19),
            '6 a 10': (20, 21, 22),
            '11 a 14': (23, 24, 25),
            '15 a 16': (26, 27, 28),
            '17 a 21': (29, 30, 31),
        },
        2020: {
            '6 a 21': (33, 34, 35),
            '6 a 10': (36, 37, 38),
            '11 a 14': (39, 40, 41),
            '15 a 16': (42, 43, 44),
            '17 a 21': (45, 46, 47),
        },
        2021: {
            '6 a 21': (49, 50, 51),
            '6 a 10': (52, 53, 54),
            '11 a 14': (55, 56, 57),
            '15 a 16': (58, 59, 60),
            '17 a 21': (61, 62, 63),
        },
        2022: {
            '6 a 21': (65, 66, 67),
            '6 a 10': (68, 69, 70),
            '11 a 14': (71, 72, 73),
            '15 a 16': (74, 75, 76),
            '17 a 21': (77, 78, 79),
        },
        2023: {
            '6 a 21': (81, 82, 83),
            '6 a 10': (84, 85, 86),
            '11 a 14': (87, 88, 89),
            '15 a 16': (90, 91, 92),
            '17 a 21': (93, 94, 95),
        },
        2024: {
            '6 a 21': (97, 98, 99),
            '6 a 10': (100, 101, 102),
            '11 a 14': (103, 104, 105),
            '15 a 16': (106, 107, 108),
            '17 a 21': (109, 110, 111),
        }
    }

    # Extraer y organizar los datos
    data = []
    for año in años:
        for grupo in grupos:
            if grupo in column_indices[año]:
                col_total, col_asisten, col_pct = column_indices[año][grupo]
                for _, row in df_raw.iterrows():
                    region = str(row['region']).strip()

                    total = row.iloc[col_total]
                    asisten = row.iloc[col_asisten]
                    pct_raw = row.iloc[col_pct]

                    # Limpiar y convertir porcentaje
                    try:
                        pct_str = str(pct_raw).strip()
                        if ',' in pct_str and '.' not in pct_str:
                            pct_str = pct_str.replace(',', '.')
                        porcentaje = round(float(pct_str), 1)

                        if porcentaje > 100:
                            porcentaje = None
                    except:
                        porcentaje = None

                    data.append({
                        'region': region,
                        'año': año,
                        'grupo_de_edad': grupo,
                        'personas_totales': total,
                        'personas_que_asisten': asisten,
                        'porcentaje_asistencia': porcentaje
                    })

    # Exportar como CSV
    df_final = pd.DataFrame(data)
    csv_buffer = io.StringIO()
    df_final.to_csv(csv_buffer, index=False)
    s3.put_object(
        Bucket=bucket_silver,
        Key=output_key,
        Body=csv_buffer.getvalue().encode('utf-8-sig')
    )

    return {
        'statusCode': 200,
        'body': f'Archivo limpio guardado en s3://{bucket_silver}/{output_key}'
    }

