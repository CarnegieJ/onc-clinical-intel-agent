"""
FILENAME: bronze_to_silver_etl.py
DESCRIPTION: PySpark logic to transform raw cBioPortal files into Delta Tables.
DEPLOYMENT: Copy this code into a Microsoft Fabric Notebook.
"""

# ---------------------------------------------------------
# COPY BELOW THIS LINE INTO FABRIC
# ---------------------------------------------------------

import tarfile
import os
import logging
from glob import glob
from pyspark.sql.functions import input_file_name, regexp_extract, col

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# The "Lakehouse" mount point is standard in Fabric
BASE_PATH = "/lakehouse/default/Files"
RAW_PATH = f"{BASE_PATH}/Raw/cBioPortal"
EXTRACT_PATH = f"{BASE_PATH}/Staging/Clinical"

# --- STEP 1: UNPACK (Standard Python) ---
# Spark cannot read inside .tar.gz files easily, so we unzip them first.
logger.info("Step 1: Extracting Clinical Data from Archives...")
os.makedirs(EXTRACT_PATH, exist_ok=True)

# Find all uploaded tar.gz files
archives = glob(f"{RAW_PATH}/*/*.tar.gz")

if not archives:
    logger.error("No files found! Did you run the ingestion pipeline?")
else:
    for archive in archives:
        try:
            # Create a readable ID from the folder name
            study_id = os.path.basename(os.path.dirname(archive))
            
            with tarfile.open(archive, "r:gz") as tar:
                for member in tar.getmembers():
                    # We only extract the 'patient' data file
                    if "data_clinical_patient.txt" in member.name:
                        # Rename it to avoid collisions (e.g., study1_patient.txt)
                        member.name = f"{study_id}_patient_data.txt" 
                        tar.extract(member, path=EXTRACT_PATH)
                        logger.info(f"Extracted: {member.name}")
        except Exception as e:
            logger.warning(f"Error reading {archive}: {e}")

# --- STEP 2: LOAD & CLEAN (PySpark) ---
logger.info("Step 2: Loading into Delta Table...")

# cBioPortal files have comments starting with '#'. We tell Spark to ignore them.
df = spark.read.option("header", "true") \
    .option("delimiter", "\t") \
    .option("comment", "#") \
    .option("inferSchema", "true") \
    .csv(f"{EXTRACT_PATH}/*.txt")

# Add the 'Study_ID' column by extracting it from the filename
df_enriched = df.withColumn("SourceFile", input_file_name()) \
                .withColumn("Study_ID", regexp_extract(col("SourceFile"), r".*/(.*)_patient_data.txt", 1)) \
                .drop("SourceFile")

# Clean Column Names (Remove spaces/parentheses for database compatibility)
for name in df_enriched.columns:
    clean_name = name.replace(" ", "_").replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    df_enriched = df_enriched.withColumnRenamed(name, clean_name)

# --- STEP 3: WRITE TO SILVER ---
table_name = "Clinical_Patients_Silver"
df_enriched.write.format("delta").mode("overwrite").saveAsTable(table_name)

logger.info(f"Success! Data saved to Delta Table: '{table_name}'")
logger.info(f"Total Records: {df_enriched.count()}")

# Show a sample
display(df_enriched.limit(8))