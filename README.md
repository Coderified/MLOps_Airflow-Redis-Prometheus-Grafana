# RF Classification Pipeline with Full-Stack Monitoring and Drift Detection

![Project Overview](images/project_architecture.png)

> A Random Forest classification system featuring ETL orchestration, imbalance correction, real-time drift detection, and a complete observability stack.

---

## 🚀 Project Description

This project demonstrates an end-to-end machine learning pipeline for a **Random Forest (RF) classification task**, supported by a robust data engineering and MLOps stack:

- **Astro Airflow**: Orchestrates the ETL pipeline for data preprocessing and ingestion.
- **psycopg2**: Interfaces with PostgreSQL for data storage.
- **SMOTE**: Corrects class imbalance in the training dataset.
- **Redis**: Stores computed features in-memory for fast access.
- **Flask**: Serves the trained model via a RESTful API.
- **alibi-detect**: Continuously monitors input data for distributional drift.
- **Docker**: Containerizes the entire stack for reproducibility and deployment.
- **Prometheus**: Scrapes runtime metrics from the Flask app at defined intervals.
- **Grafana**: Visualizes metrics collected by Prometheus via interactive dashboards.

---


## 🛠️ Tech Stack

| Component       | Tool              |
|----------------|-------------------|
| Orchestration   | Astro Airflow      |
| Data Storage    | PostgreSQL + psycopg2 |
| Imbalance Fix   | SMOTE              |
| Model Serving   | Flask              |
| Feature Cache   | Redis              |
| Drift Detection | alibi-detect       |
| Containerization| Docker             |
| Monitoring      | Prometheus + Grafana |

---

## 📈 Monitoring Setup

- Prometheus is configured to scrape the Flask app's `/metrics` endpoint every 15 seconds.
- Grafana dashboards visualize real-time API latency, request rates, drift status, and custom metrics.
