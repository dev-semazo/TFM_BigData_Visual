import json
import boto3
import pandas as pd
import numpy as np
import pmdarima as pm
import time
import io
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

def get_data():
    '''
    Obtiene datos de nacimientos de Colombia desde Athena y los procesa.

    Esta función:
    1. Se conecta a Amazon Athena y ejecuta una consulta para obtener datos de nacimientos
    2. Espera a que la consulta se complete
    3. Procesa los resultados y los convierte en un DataFrame
    4. Realiza transformaciones en los datos:
       - Convierte la columna año a datetime
       - Agrupa por año y municipio
       - Separa el código del nombre del municipio
       - Renombra columnas

    Returns:
    --------
    DataFrame con las siguientes columnas:
    - año: fecha del registro
    - municipio: nombre del municipio
    - nacimientos: total de nacimientos
    '''
    athena_client = boto3.client('athena', region_name='us-east-1')
    query = "SELECT * FROM nacimientos_colombia_limpio;"
    # Start Athena query
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'tfm-educ-app-silver'},
        WorkGroup = 'tfm-educ-app-athena'
    )
    query_execution_id = response['QueryExecutionId']
    
    while True:
        status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED']:
            break
        time.sleep(2)
    if status == 'SUCCEEDED':
        # Get query results
        result_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        data = []
        columns = None
        next_token = None
        
        while True:
            if columns is None:
                columns = [col["VarCharValue"] for col in result_response["ResultSet"]["Rows"][0]["Data"]]
            if next_token:
                result_response = athena_client.get_query_results(QueryExecutionId=query_execution_id, NextToken=next_token)
            for row in result_response["ResultSet"]["Rows"][1:]:
                data.append([col.get("VarCharValue", None) for col in row["Data"]])
            next_token = result_response.get("NextToken")
            if not next_token:
                break 
        df = pd.DataFrame(data, columns=columns)
        df['año'] = pd.to_datetime(df['año'].astype(str))
        df['total general'] = df['total general'].astype(int) 

        #Estandarizar Municipios
        loc_0 = df.columns.get_loc('municipio')
        df_split = df['municipio'].str.split(pat='^\\d+\\s+', expand=True).add_prefix('municipio_')
        df = pd.concat([df.iloc[:, :loc_0], df_split, df.iloc[:, loc_0:]], axis=1)
        df = df.drop(columns=['municipio', 'municipio_0'])
        df = df.rename(columns={'municipio_1': 'municipio', 'total general' : 'nacimientos'})
        df['municipio'] = df['municipio'].str.lower()

        #Información Agrupada
        df = df.groupby(['departamento', 'municipio', 'año'])['nacimientos'].sum().reset_index()
        df = df.groupby(['departamento', 'año'])['nacimientos'].sum().reset_index()
        
        logger.info(f'DF Procesado: {df.head()}')
        return df
    elif status == 'FAILED':
        raise Exception("Athena query failed")

def run_model(df, n_periodos_a_predecir=5):
    '''
        Ejecuta un modelo ARIMAX para predecir nacimientos para múltiples Departamento

        Parámetros:
        -----------
        n_periodos_a_predecir : int, default=5
            Número de periodos futuros a predecir

        La función:
        1. Itera a través de cada Departamento en el conjunto de datos
        2. Crea un modelo de series temporales con una variable indicadora de pandemia
        3. Ajusta un modelo ARIMAX usando auto_arima
        4. Hace predicciones para periodos futuros
        5. Combina datos históricos y predichos
        6. Retorna un dataframe con resultados para todos los Departamento

        Returns:
        --------
        DataFrame que contiene:
        - Nombre del Departamento
        - Año
        - Tipo (Real vs Predicción)
        - Número de nacimientos
        - Intervalos de confianza para predicciones
        - Orden del modelo ARIMA
        - Puntaje AIC    
    '''
    lista_de_resultados = []
    df_real = pd.DataFrame()
    ultimo_anio_conocido = df['año'].max()
    departamentos = df['departamento'].unique()
    for departamento in departamentos:
        df_departamento = df[df['departamento'] == departamento].copy()
        if df_departamento['año'].max() == ultimo_anio_conocido:
            if len(df_departamento) < 10: # Umbral mínimo de puntos de datos
                logger.info(f"Datos insuficientes para {departamento}. Se omite el modelo.")
                continue # Salta a la siguiente iteración del bucle
            logger.info(df_departamento)
            df_departamento = df_departamento.set_index('año')
            df_departamento.index.freq = 'YS'
            y = df_departamento['nacimientos']
            X = pd.DataFrame(index=y.index)
            X['Pandemia'] = 0
            X.loc['2020-01-01':'2022-01-01', 'Pandemia'] = 1
            logger.info(f"--- Entrenando modelo ARIMAX para el Departamento: {departamento} ---")
            arimax_model = pm.auto_arima(y, X=X,
                                        seasonal=False,
                                        trace=True, # Muestra el proceso de búsqueda
                                        error_action='ignore',
                                        suppress_warnings=True)
            # Para el futuro, la variable 'Pandemia' vuelve a ser 0
            X_futuro = pd.DataFrame({
                'Pandemia': [0] * n_periodos_a_predecir
            }, index=pd.date_range(start=ultimo_anio_conocido, periods=n_periodos_a_predecir+1, freq='YS')[1:])
            prediccion, conf_int = arimax_model.predict(n_periods=n_periodos_a_predecir, X=X_futuro, return_conf_int=True)
            logger.info(f"\n--- PREDICCIÓN MODELO {departamento}---")
            logger.info(prediccion)

            df_real = pd.DataFrame({
                'departamento': departamento,
                'año': y.index,
                'tipo': 'Real',
                'nacimientos': y.values,
                'intervalo_inferior': np.nan, # No aplica para datos reales
                'intervalo_superior': np.nan, # No aplica para datos reales
                'modelo_arima': str(arimax_model.order)
            })
            df_pred = pd.DataFrame({
                'departamento': departamento,
                'año': prediccion.index,
                'tipo': 'Predicción',
                'nacimientos': prediccion.values,
                'intervalo_inferior': conf_int[:, 0],
                'intervalo_superior': conf_int[:, 1],
                'modelo_arima': str(arimax_model.order)
            })

            df_completo_departamento = pd.concat([df_real, df_pred], ignore_index=True)
            
            lista_de_resultados.append(df_completo_departamento)

    df_final_arima = pd.concat(lista_de_resultados, ignore_index=True)
    return df_final_arima

def save_results(df):
    s3 = boto3.client('s3')
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
    s3.put_object(Bucket='tfm-educ-app-gold', Key='prev_comp/resultados_arima.parquet', Body=parquet_buffer.getvalue())
    return True 

def lambda_handler(event, context):
    try:
        model_df = get_data()
        periods = event.get('periods', 5)
        
        result = run_model(model_df, periods)
        if save_results(result):
            logger.info('Model Done')
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'Model Done'})
            }
        else:
            logger.error('Failed to save results', exc_info=1)
            return {
                'statusCode': 500,
                'body': json.dumps({'status': 'Failed to save results'})
            }
    except Exception as e:
        logger.error(str(e), exc_info=1)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }