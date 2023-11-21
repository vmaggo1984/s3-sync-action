import os
import json
import pendulum
from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

topic_name = "GITHUBTESTING"

# Get SAP HANA Credentials
sm_secretId_hana = "SAPHANA_MWAA"
# Get SNOWFLAKE Credentials
sm_secretId_snowflake = "IDA_AIRFLOW_MWAA_None"

# Instantiate Pendulum and set your timezone.
local_tz = pendulum.timezone("Australia/Perth")

# Default Airflow Parameters
default_args = {
    "owner": "FMGL-Airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 10, 6, tzinfo=local_tz),
    "end_date": None,
}

with DAG(
    dag_id=os.path.basename(__file__).replace(".py", ""),
    default_args=default_args,
    max_active_runs=1,
    catchup=False,
) as dag:
    
    from custom_queries.common_config import (
        Read_Secrets_Values,
        replicationHanaData,
        on_failure_callback_ingestion,
    )

    t0 = DummyOperator(task_id="START")
    t1 = DummyOperator(task_id="END")

    read_Secrets_HANA = PythonOperator(
        task_id="read_Secrets_HANA",
        python_callable=Read_Secrets_Values,
        provide_context=True,
        on_failure_callback=on_failure_callback_ingestion,
        retries=1,
        op_kwargs={"sm_secretId_name": sm_secretId_hana},
    )

    read_Secrets_Snowflake = PythonOperator(
        task_id="read_Secrets_Snowflake",
        python_callable=Read_Secrets_Values,
        provide_context=True,
        on_failure_callback=on_failure_callback_ingestion,
        retries=1,
        op_kwargs={"sm_secretId_name": sm_secretId_snowflake},
    )

    for metadatalist in list(
        json.loads(
            Variable.get("ingestion_table_names_{}".format(topic_name)).replace(
                "'", '"'
            )
        )
    ):
        repl_hana_ingestion = PythonOperator(
            task_id="{}_Ingestion_{}".format(topic_name, metadatalist[0]).replace(
                ".", "_"
            ),
            python_callable=replicationHanaData,
            provide_context=True,
            on_failure_callback=on_failure_callback_ingestion,
            pool="INGESTION",
            retries=1,
            op_kwargs={
                "table": metadatalist[0],
                "limit": metadatalist[1],
                "chunksize": metadatalist[2],
                "targetschemaname": metadatalist[3],
                "sourceschemaname": metadatalist[4],
                "type": metadatalist[5],
            },
        )

        t0.set_downstream(read_Secrets_HANA)
        read_Secrets_HANA.set_downstream(read_Secrets_Snowflake)
        read_Secrets_Snowflake.set_downstream(repl_hana_ingestion)
        repl_hana_ingestion.set_downstream(t1)