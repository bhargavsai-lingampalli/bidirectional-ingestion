from flask import Flask, request, jsonify, render_template
from flatfile_handler import FlatFileHandler
from clickhouse_client import ClickHouseClient
import pandas as pd
from dotenv import load_dotenv
import os


load_dotenv()

# Get the values from the environment
host = os.getenv('CLICKHOUSE_HOST')
port = int(os.getenv('CLICKHOUSE_PORT'))
db = os.getenv('CLICKHOUSE_DB')
user = os.getenv('CLICKHOUSE_USER')
password = os.getenv('CLICKHOUSE_PASSWORD')


app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/connect_clickhouse", methods=["POST"])
def connect_clickhouse():
    data = request.json
    try:
        ch = ClickHouseClient(**data)
        tables = ch.get_tables()
        return jsonify({"status": "success", "tables": tables})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/load_columns", methods=["POST"])
def load_columns():
    try:
        data = request.json
        print("Received data:", data)  # Debug log
        source_type = data.get("source_type")
        if not source_type:
            return jsonify({"status": "error", "message": "'source_type' is required"})

        if source_type == "ClickHouse":
            # Ensure 'conn' and 'table' are present
            conn = data.get("conn")
            table = data.get("table")

            if not conn or not table:
                return jsonify({"status": "error", "message": "'conn' and 'table' are required for ClickHouse"}), 401
            
            ch = ClickHouseClient(**conn)
            columns = ch.get_columns(table)
            print(columns)
            return jsonify({"status": "success", "columns": columns})
        
        elif source_type == "FlatFile":
            # Ensure 'filename' is present for FlatFile
            if "filename" not in data:
                return jsonify({"status": "error", "message": "'filename' is required for FlatFile"}), 402
            
            file_handler = FlatFileHandler(data['filename'], data.get('delimiter', ','))
            df = file_handler.read()
            columns = df.columns.tolist()
            return jsonify({"status": "success", "columns": columns})
        
        else:
            return jsonify({"status": "error", "message": "Invalid source_type"}), 403

    except Exception as e:
        print(str(e))
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/load_flatfile_columns", methods=["POST"])
def load_flatfile_columns():
    try:
        # Assuming data is being sent in JSON format
        data = request.json
        print(data)  # Debug log
        filename = data.get("filename")
        delimiter = data.get("delimiter", ",")
        print(filename)
        # Load and process the flat file (use pandas or any library to read the file)
        df = pd.read_csv(filename, delimiter=delimiter)

        # Get columns from the dataframe
        columns = df.columns.tolist()
        return jsonify({"status": "success", "columns": columns})

    except Exception as e:
        print(str(e))
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/start_ingestion", methods=["POST"])
def start_ingestion():
    try:
        data = request.json
        columns = data.get("columns")
        source = data.get("source")
        destination = data.get("destination")

        print(data)
        if source == "clickhouse" and destination == "flatfile":
            conn = data.get("conn")
            table = data.get("table")
            filename = f'{table}.csv'
            # Fetch data from ClickHouse and export to flat file
            ch = ClickHouseClient(**conn)
            query = f"SELECT {','.join(columns)} FROM {table} LIMIT 1000000"
            df = ch.client.query_df(query)
            df.to_csv(filename, index=False)
            return jsonify({"status": "success", "message": f"Exported {len(df)} rows to {table}.csv"})

        elif source == "flatfile" and destination == "clickhouse":
            filename = data.get("filename")
            delimiter = data.get("delimiter", ",")
            table = data.get("table")
            conn = data.get("conn", {})  # optional if already connected

            # Read data from flat file and ingest into ClickHouse
            ff = FlatFileHandler(filename, delimiter)
            df = ff.read(columns)

            # Connect to ClickHouse and create table if not exists
            ch = ClickHouseClient(host, port, db, user, password)
            print(filename)
            ch.import_from_dataframe(df, str(filename[:-4]))
            print(f"Imported {len(df)} rows into ClickHouse table '{filename[:-4]}'.")
            return jsonify({"status": "success", "message": f"Ingested {len(df)} rows into ClickHouse table '{filename[:-4]}'."})
        
        else:
            return jsonify({"error": "Invalid source/destination pair"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
