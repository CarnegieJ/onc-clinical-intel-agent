# 🏥 Clinical Intelligence Agent (Backend Demo)

![Status](https://img.shields.io/badge/Status-Prototype-green)
![Tech Stack](https://img.shields.io/badge/Azure-Fabric%20%7C%20AI%20Foundry%20%7C%20Python-blue)

**Author:** [Carnegie Johnson/IAYF Consulting]  
**License:** MIT (Attribution Required)

## 🎯 Executive Summary
This repository demonstrates the **Backend Architecture** for a secure Clinical Decision Support Agent. Designed for high-compliance healthcare environments, it integrates **Microsoft Fabric (OneLake)** for data storage with **Azure AI** for secure inference.

Unlike standard chatbots, this architecture prioritizes:
1.  **Data Lineage:** Traceable ETL pipelines from public sources (cBioPortal) to Silver Delta Tables.
2.  **Clinical Validity:** Statistical checks for "Artificial Capping" and outliers before inference.
3.  **Safety First:** A dedicated Middleware layer that sanitizes PII (Protected Health Information) *before* it reaches the LLM.

---

## 🏗️ Architecture
### **Architecture Insight: The Medallion Model**
In Data Engineering, best practice is the **Medallion Architecture**:
* **🥉 Bronze Layer (Raw):** Raw `.tar.gz` files sitting in a folder. They are hard to query and "messy."
* **🥈 Silver Layer (Clean):** Clean the headers, and organize them into **Delta Tables** (high-performance SQL tables).
* **🥇 Gold Layer (Curated):** Aggregated data ready for dashboards and AI agents.

1. **Ingestion Layer (Phase 1):** Python scripts fetch raw `.tar.gz` archives from cBioPortal and stream them into **Microsoft OneLake**.

<table style="border-collapse: collapse;">
    <tr>
        <td style="border: 1px solid #ddd; padding: 6px; text-align:center;">
            <img src="img/pic03.png" alt="Data summary" style="max-width:100%; height:auto;" />
        </td>
        <td style="border: 1px solid #ddd; padding: 6px; text-align:center;">
            <img src="img/pic05.png" alt="Data distribution" style="max-width:100%; height:auto;" />
        </td>
    </tr>
</table>

2. **Processing Layer (Fabric):** PySpark notebooks transform raw files into queryable **Delta Tables** (Silver Layer).

<table style="border-collapse: collapse;">
    <tr>
        <td style="border: 1px solid #ddd; padding: 6px; text-align:center;">
            <img src="img/pic02.png" alt="Delta Table" style="max-width:100%; height:auto;" />
        </td>
        <td style="border: 1px solid #ddd; padding: 6px; text-align:center;">
            <img src="img/pic06.png" alt="Lakehouse" style="max-width:100%; height:auto;" />
        </td>
    </tr>
</table>

3. **Analysis Layer (Phase 2):** Local Python (VS Code) connects via **ODBC/SQL** to validate data distributions.
![Age vs Survival](img/pic04.png)

4. **Safety Layer (Phase 3):** A Hybrid Guardrails system uses Regex + Azure Content Safety to block toxic or PII-laden prompts.

---

## ⚙️ Configuration & Setup

### **Prerequisites:**
* **Azure** accoount
* **Microsoft Frabric** workspace
* **Python 3.10+**
* **Visual Studio Code** (Jupyter notebooks)
* **Azure CLI:** Run `az login` to authenticate.
* **ODBC Driver:** You **MUST** install the [ODBC Driver 18 for SQL Server](https://go.microsoft.com/fwlink/?linkid=2249006) for Phase 2 to work.

### **1. Clone & Environment**
To get started quickly, we provide a template for your environment variables.

1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/CarnegieJ/onc-clinical-intel-agent/](https://github.com/CarnegieJ/onc-clinical-intel-agent)[CarnegieJ]/clinical-intelligence-agent.git
    cd clinical-intelligence-agent
    ```

2.  **Configure Secrets:**
    * Locate the file named `.env.template` in the root directory.
    * **Rename** it to `.env`.
    * Open it and fill in your specific Azure values (Workspace ID, Connection Strings, etc.).

    ```bash
    # Example Command (Terminal)
    cp .env.template .env
    ```
