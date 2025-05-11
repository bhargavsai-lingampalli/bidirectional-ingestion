## Bidirectional ClickHouse ↔ Flat File Ingestion Tool

### Overview

This project provides a web-based application to facilitate bidirectional data ingestion between a ClickHouse database and flat files (CSV). It supports:

- **ClickHouse → Flat File** export
- **Flat File → ClickHouse** import
- JWT token–based authentication for ClickHouse
- Schema discovery and column selection
- Record count reporting upon job completion
- Optional multi-table join ingestion (bonus)

### Features

- RESTful API built with Flask
- Simple frontend (HTML/JS) for user interactions
- ClickHouse client integration via `clickhouse-connect`
- Flat file handling with `pandas`
- Column-wise selection and data preview
- Error handling with user-friendly messages
- Configurable via environment variables or UI inputs

---

### Prerequisites

- Python 3.8+
- `pip` for Python package management
- A running ClickHouse instance (local Docker or cloud)
- Node.js (optional, if extending frontend build tools)

---

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/bhargavsai-lingampalli/bidirectional-ingestion.git
   cd bidirectional-ingestion
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create a `.env` file in the `main/` folder with the following keys:

   ```ini
   CH_HOST=your_clickhouse_host
   CH_PORT=9440
   CH_DATABASE=default
   CH_USER=default
   CH_JWT_TOKEN=your_jwt_token
   ```

---

### Running the Application

1. **Start the main**

   ```bash
   cd main
   flask run --host=0.0.0.0 --port=5000
   ```

2. **Open the frontend**
   Open `frontend/index.html` in your browser (no build step required for vanilla JS).

---

### Usage

1. **Connect to ClickHouse**: Fill in connection fields and hit **Connect**.
2. **Load Tables**: Select a table to list columns.
3. **Select Columns**: Check desired columns for ingestion.
4. **Export to CSV**: Click **Start Export** to save selected data.
5. **Import CSV**: Upload or specify CSV file, select columns, and click **Import**.
6. **View Results**: Record counts and status updates appear on the UI.

---

### Testing

Use provided example datasets from ClickHouse:

1. **uk\_price\_paid** → Export to `uk_price_paid.csv` and verify record count.
2. **CSV → ClickHouse**: Import sample CSV, confirm new table creation and row count.
3. **Error Scenarios**: Test invalid credentials, unreachable hosts, malformed CSV.
4. **(Bonus)** Multi-table JOIN ingestion: configure JOIN keys and validate exported data.

---


### Contributing

Feel free to fork, open issues, or submit pull requests. For major changes, please open an issue first to discuss your ideas.

---

**Enjoy building your data pipelines!**

