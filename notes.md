# Notes

## Week1

```bash
python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5435 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips
```

## Week2

### Installing Kestra using Docker Compose.

Download the Docker Compose file using the following command:

```bash
curl -o docker-compose.yml \
https://raw.githubusercontent.com/kestra-io/kestra/develop/docker-compose.yml
```

Launch Kestra using the following command.

```bash
docker-compose up -d
```

[Repo with data](https://github.com/DataTalksClub/nyc-tlc-data)

```yml
id: postgres_taxi
namespace: zoomcamp

inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: ['yellow', 'green']
    defaults: 'yellow'

  - id: year
    type: SELECT
    displayName: Select year
    values: ["2019", "2020"]
    defaults: '2019'
  
  - id: month
    type: SELECT
    displayName: Select month
    values: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    defaults: '01'

variables:
  file: "{{ inputs.taxi }}_tripdata_{{ inputs.year }}-{{ inputs.month }}.csv"
  staging_table: "public.{{ inputs.taxi }}_tripdata_staging"
  table: "public.{{ inputs.taxi }}_tripdata"
  data: "{{ outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ inputs.year ~ '-' ~ inputs.month ~ '.csv'] }}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{ render(vars.file) }}"
      taxi: "{{ inputs.taxi }}"

  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{ inputs.taxi }}/{{ render(vars.file) }}.gz | gunzip > {{ render(vars.file) }}

  - id: green_create_table
    type: io.kestra.plugin.jdbc.postgresql.Queries
    sql: |
      CREATE TABLE IF NOT EXISTS {{ render(vars.table) }}
      (
          unique_row_id TEXT,
          filename TEXT,
          vendorid bigint,
          lpep_pickup_datetime timestamp without time zone,
          lpep_dropoff_datetime timestamp without time zone,
          store_and_fwd_flag text COLLATE pg_catalog."default",
          RatecodeID bigint,
          PULocationID bigint,
          DOLocationID bigint,
          passenger_count bigint,
          trip_distance double precision,
          fare_amount double precision,
          extra double precision,
          mta_tax double precision,
          tip_amount double precision,
          tolls_amount double precision,
          ehail_fee double precision,
          improvement_surcharge double precision,
          total_amount double precision,
          payment_type bigint,
          trip_type double precision,
          congestion_surcharge double precision
      )

  - id: green_create_staging_table
    type: io.kestra.plugin.jdbc.postgresql.Queries
    sql: |
      CREATE TABLE IF NOT EXISTS {{ render(vars.staging_table) }}
      (
          unique_row_id TEXT,
          filename TEXT,
          vendorid bigint,
          lpep_pickup_datetime timestamp without time zone,
          lpep_dropoff_datetime timestamp without time zone,
          store_and_fwd_flag text COLLATE pg_catalog."default",
          RatecodeID bigint,
          PULocationID bigint,
          DOLocationID bigint,
          passenger_count bigint,
          trip_distance double precision,
          fare_amount double precision,
          extra double precision,
          mta_tax double precision,
          tip_amount double precision,
          tolls_amount double precision,
          ehail_fee double precision,
          improvement_surcharge double precision,
          total_amount double precision,
          payment_type bigint,
          trip_type double precision,
          congestion_surcharge double precision
      )
  

    # sql: |
    #   CREATE TABLE {{ render(vars.table) }} (
    #     unique_row_id TEXT,
    #     filename TEXT,
    #     "VendorID" BIGINT, 
    #     tpep_pickup_datetime TIMESTAMP WITHOUT TIME ZONE, 
    #     tpep_dropoff_datetime TIMESTAMP WITHOUT TIME ZONE, 
    #     passenger_count BIGINT, 
    #     trip_distance FLOAT(53), 
    #     "RatecodeID" BIGINT, 
    #     store_and_fwd_flag TEXT, 
    #     "PULocationID" BIGINT, 
    #     "DOLocationID" BIGINT, 
    #     payment_type BIGINT, 
    #     fare_amount FLOAT(53), 
    #     extra FLOAT(53), 
    #     mta_tax FLOAT(53), 
    #     tip_amount FLOAT(53), 
    #     tolls_amount FLOAT(53), 
    #     improvement_surcharge FLOAT(53), 
    #     total_amount FLOAT(53), 
    #     congestion_surcharge FLOAT(53)
    #   )
  
  - id: green_copy_in_to_staging_table
    type: io.kestra.plugin.jdbc.postgresql.CopyIn
    format: CSV
    from: "{{render(vars.data)}}"
    table: "{{render(vars.staging_table)}}"
    header: true
    columns: [VendorID, lpep_pickup_datetime, lpep_dropoff_datetime,    store_and_fwd_flag,RatecodeID,PULocationID,DOLocationID,    passenger_count,trip_distance,fare_amount,extra,mta_tax,tip_amount,tolls_amount,ehail_fee,improvement_surcharge,total_amount,payment_type,trip_type,congestion_surcharge]
  - id: green_add_unique_id_and_filename
    type: io.kestra.plugin.jdbc.postgresql.Queries
    sql: |
      UPDATE {{render(vars.staging_table)}}
      SET
        unique_row_id = md5(
          COALESCE(CAST(VendorId AS text), '') || ||
          COALESCE(CAST(lpep_pickup_datetime AS text), '') ||
          COALESCE(CAST(lpep_dropoff_datetime AS text), '') ||
          '' ||
          COALESCE(PULocationID, '') ||
          COALESCE(DOLocationID, '') ||
          COALESCE(CAST(fare_amount AS text), '') ||
          COALESCE(CAST(trip_distance AS text), '')
        ), filename = '{{render(vars.file)}}';


pluginDefaults:
  - type: io.kestra.plugin.jdbc.postgresql
    values:
      url: jdbc:postgresql://host.docker.internal:5437/postgres-zoomcamp
      username: kestra
      password: k3str4
```
