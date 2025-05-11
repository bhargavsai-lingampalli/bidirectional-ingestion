let selectedTable = null;
let selectedColumns = [];
let clickhouseConn = {};

document.getElementById("sourceSelect").addEventListener("change", toggleForms);
document.getElementById("destinationSelect").addEventListener("change", toggleForms);

function toggleForms() {
    const source = document.getElementById("sourceSelect").value;
    const chForm = document.getElementById("clickhouseForm");
    const flatForm = document.getElementById("flatFileForm");

    chForm.style.display = source === "clickhouse" ? "block" : "none";
    flatForm.style.display = source === "flatfile" ? "block" : "none";
}

document.getElementById("connectForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const conn = {
        host: document.getElementById("host").value,
        port: document.getElementById("port").value,
        database: document.getElementById("db").value,
        username: document.getElementById("user").value,
        jwt_token: document.getElementById("token").value
    };
    clickhouseConn = conn;

    const response = await fetch("/connect_clickhouse", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(conn)
    });

    const data = await response.json();
    if (data.status === "success") {
        const list = document.getElementById("tablesList");
        list.innerHTML = `
            <h4>Select Table:</h4>
            <select id="tableDropdown">
                <option value="">-- Select Table --</option>
                ${data.tables.map(table => `<option value="${table}">${table}</option>`).join("")}
            </select>
        `;
        
        document.getElementById("tableDropdown").addEventListener("change", (e) => {
            const selected = e.target.value;
            if (selected) {
                loadColumnsFromClickHouse(selected);
            } else {
                document.getElementById("columnSelectionArea").style.display = "none";
            }
        });
        
    } else {
        alert(data.message);
    }
});


async function loadColumnsFromClickHouse(table) {
    selectedTable = table;

    const response = await fetch("/load_columns", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            source_type: 'ClickHouse',
            conn: clickhouseConn,
            table: table
        })
    });

    const data = await response.json();

    if (data.status !== "success") {
        alert(data.message || "Failed to load columns");
        return;
    }

    const columns = data.columns;
    const form = document.getElementById("columnForm");
    form.innerHTML = ""; // Clear previous columns

    columns.forEach(col => {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "columns";
        checkbox.value = col;
        checkbox.checked = true;  // Optional: auto-check all

        const label = document.createElement("label");
        label.textContent = col;
        label.style.marginRight = "10px";

        form.appendChild(checkbox);
        form.appendChild(label);
        form.appendChild(document.createElement("br"));
    });

    document.getElementById("columnSelectionArea").style.display = "block";
}



document.getElementById("loadFlatColumns").addEventListener("click", async () => {
    const filename = document.getElementById("flatFilename").value;
    const delimiter = document.getElementById("flatDelimiter").value;

    const response = await fetch("/load_flatfile_columns", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filename, delimiter })
    });

    const columns = await response.json();
    const form = document.getElementById("columnForm");
    form.innerHTML = "";
    columns.forEach(col => {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "columns";
        checkbox.value = col;

        const label = document.createElement("label");
        label.textContent = col;

        form.appendChild(checkbox);
        form.appendChild(label);
        form.appendChild(document.createElement("br"));
    });

    document.getElementById("columnSelectionArea").style.display = "block";
});

// document.getElementById("startIngestion").addEventListener("click", async () => {
//     const columns = [...document.querySelectorAll("input[name='columns']:checked")].map(cb => cb.value);
//     const source = document.getElementById("sourceSelect").value;
//     const destination = document.getElementById("destinationSelect").value;

//     let payload = { columns, source, destination };
//     document.getElementById("statusArea").innerText = "Starting ingestion...";

//     if (source === "clickhouse") {
//         payload = {
//             ...payload,
//             conn: clickhouseConn,
//             table: selectedTable,
//             filename: "exported.csv"  // This can be made dynamic later
//         };
//     } else if (source === "flatfile") {
//         payload = {
//             ...payload,
//             filename: document.getElementById("flatFilename").value,
//             delimiter: document.getElementById("flatDelimiter").value,
//             table: "imported_data"  // Target table name for ClickHouse
//         };
//     }

//     const response = await fetch("/start_ingestion", {
//         method: "POST",
//         headers: {'Content-Type': 'application/json'},
//         body: JSON.stringify(payload)
//     });

//     const result = await response.json();
//     document.getElementById("statusArea").innerText = result.message || result.error;
// });
