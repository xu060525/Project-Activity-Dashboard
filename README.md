# Project Health Dashboard (Local-First)

A desktop-grade analytics tool designed to quantify the "health" and sustainability of GitHub repositories. Built with **Python**, **Streamlit**, and **SQLite**.

> **Key Difference**: Unlike standard metrics, this tool calculates a proprietary **Health Score (0-100)** based on *Bus Factor*, *Code Churn*, and *Activity Frequency*.

---

## Key Features

*   **Risk Quantification**: Automatically detects single-point-of-failure risks (Bus Factor).
*   **Local-First Architecture**: Data is cached locally in SQLite. Incremental syncing ensures sub-second query speeds after the first fetch.
*   **Privacy Focused**: Your tokens and private repo data never leave your local machine.
*   **Interactive Visualization**: Analyze trends, contributor diversity, and weekly work rhythm.

## Tech Stack

*   **Core**: Python 3.11, Streamlit
*   **Data**: Pandas, SQLite (NoSQL-free architecture)
*   **Visualization**: Altair, Streamlit Charts
*   **Engineering**: Multithreading (implied via Streamlit execution model), Incremental Caching

## Quick Start

### Option A: One-Click Start (Windows)
Double-click `Start_App.bat` in the root folder.

### Option B: For Developers
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure Secrets:
   Create `.streamlit/secrets.toml` and add your GitHub Token:
   ```toml
   GITHUB_TOKEN = "your_token_here"
   ```
3. Run:
   ```bash
   python main_launcher.py
   ```