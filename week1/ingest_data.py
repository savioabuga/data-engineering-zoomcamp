import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
from time import time

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name

    csv_name = 'yellow_tripdata_2021-01.csv'   

    # Create a connection to the PostgreSQL database
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # Read the CSV file in chunks
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Get the first chunk
    df = next(df_iter)
    
    # Convert datetime columns to datetime objects
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Create the table in the database (replace if it exists)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    # Insert the first chunk of data
    df.to_sql(name=table_name, con=engine, if_exists="append")


    while True:
        start_time = time()
        try:
            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name=table_name, con=engine, if_exists="append")

            print(f"inserted another chunk...{(time() - start_time):.2f}")
        except StopIteration:
            print("Finished ingesting data.")
            break

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")
    parser.add_argument("--user", help="User name for Postgres")
    parser.add_argument("--password", help="Password for Postgres")
    parser.add_argument("--host", help="Host for Postgres")
    parser.add_argument("--port", help="Port for Postgres", default="5432")
    parser.add_argument("--db", help="Database name")
    parser.add_argument("--table_name", help="Name of the table where we will write the results")

    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(args)


