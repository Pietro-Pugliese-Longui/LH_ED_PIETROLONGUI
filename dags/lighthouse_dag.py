from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from docker.types import Mount
import os
import shutil

default_args={

}

def create_tables(**context):
    #Este e o path do volume do container do Airflow onde serão carregados os arquivos
    dir_atual = '/opt/data/output'

    arquivos_csv = []
    for f in os.listdir(dir_atual):
        if f.endswith('.csv'):
            arquivos_csv.append(f)

    data_atual = context['ds']

    for arquivo_csv in arquivos_csv:

        if 'order_details' in arquivo_csv:
            primeira_pasta = 'csv'
        else:
            primeira_pasta = 'postgres'

        nome_arquivo = os.path.splitext(arquivo_csv)[0]

        caminho_dir = os.path.join(dir_atual, primeira_pasta)
        if not os.path.exists(caminho_dir):
            os.makedirs(caminho_dir)

        pasta_arquivo = os.path.join(caminho_dir, nome_arquivo)
        if not os.path.exists(pasta_arquivo):
            os.makedirs(pasta_arquivo)

        pasta_data = os.path.join(pasta_arquivo, data_atual)
        if not os.path.exists(pasta_data):
            os.makedirs(pasta_data)

        arquivo_final = os.path.join(dir_atual, arquivo_csv)
        dir_arquivo_final = os.path.join(pasta_data, arquivo_csv)
        shutil.move(arquivo_final, dir_arquivo_final)


with DAG (
    
    dag_id="Extração_lighthouse",
    start_date=datetime(2024,6,6),
    schedule_interval="@daily",
    catchup=False

) as dag:


    mounts = [
        Mount(
            source='/home/pietro/Documentos/desafio_engenharia_dados/data',  
            target='/opt/data',  
            type='bind',
        ),
    ]


    
    task_csv_to_csv = DockerOperator(
        task_id='csv_to_csv',
        image='desafio-meltano:v2.2',
        container_name='csv_to_csv',
        api_version= 'auto',
        docker_url="unix://var/run/docker.sock",
        auto_remove='force',
        network_mode='container:postgres',
        mount_tmp_dir=False,
        mounts=mounts,
        command="run tap-csv-order_details-to-target-csv-order_details"
    )
    

    task_postgres_to_csv = DockerOperator(
        task_id='postgres_to_csv',
        image='desafio-meltano:v2.2',
        container_name='postgres_to_csv',
        api_version= 'auto',
        docker_url="unix://var/run/docker.sock",
        auto_remove='force',
        network_mode='container:postgres',
        mount_tmp_dir=False,
        mounts=mounts,
        command="run tap-postgres-to-tap-csv"
    )
    
    task_csv_to_postgres = DockerOperator(
        task_id='csv_to_postgres',
        image='desafio-meltano:v2.2',
        container_name='csv_to_postgres',
        api_version= 'auto',
        docker_url="unix://var/run/docker.sock",
        auto_remove='force',
        network_mode='container:postgres',
        mount_tmp_dir=False,
        mounts=mounts,
        environment={'EXECUTION_DATE':"{{ ds }}"},
        command="run csv-to-postgres-finaldb"
    )
    
    
    faz_pastas = PythonOperator(
        task_id='create_tables',
        python_callable=create_tables,
        provide_context=True,
        dag=dag,
    )

    [task_csv_to_csv, task_postgres_to_csv] >> faz_pastas >> task_csv_to_postgres 
   
