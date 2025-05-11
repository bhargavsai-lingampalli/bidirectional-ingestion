import clickhouse_connect
import pandas as pd
import numpy as np

class ClickHouseClient:
    def __init__(self, host, port, database, username, jwt_token):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=username,
            password=jwt_token,
            database=database,
            secure=True
        )
        self.database = 'default'

    def get_tables(self):
        return self.client.query("SHOW TABLES").result_rows

    def get_columns(self, table):
        result = self.client.query(f"DESCRIBE TABLE {table}")
        return [row[0] for row in result.result_rows]

    def export_to_csv(self, table, columns, filename):
        cols = ",".join(columns)
        result = self.client.query(f"SELECT {cols} FROM {table}")
        df = pd.DataFrame(result.result_rows, columns=columns)
        df.to_csv(filename, index=False)
        return len(df)

    def import_from_dataframe(self, df, table_name):
        # Drop the table if it already exists
        self.client.command(f"DROP TABLE IF EXISTS {table_name}")

        # Dynamically generate column types based on DataFrame dtypes
        column_definitions = []
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_bool_dtype(dtype):
                col_type = "UInt8"
            elif pd.api.types.is_integer_dtype(dtype):
                col_type = "Int64"
            elif pd.api.types.is_float_dtype(dtype):
                col_type = "Float64"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                col_type = "DateTime"
            else:
                col_type = "String"
            column_definitions.append(f"{col} {col_type}")

        create_table_query = (
            f"CREATE TABLE IF NOT EXISTS {table_name} "
            f"({', '.join(column_definitions)}) "
            "ENGINE = MergeTree() ORDER BY tuple()"
        )

        # Create the table
        self.client.command(create_table_query)

        # Clean and convert the DataFrame before insertion
        for col in df.columns:
            if pd.api.types.is_bool_dtype(df[col]):
                df[col] = df[col].astype(int)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("").astype(str)

        # Insert the data into the ClickHouse table
        self.client.insert(
            table=table_name,
            data=df.values.tolist(),
            column_names=list(df.columns)
        )

        return len(df)


