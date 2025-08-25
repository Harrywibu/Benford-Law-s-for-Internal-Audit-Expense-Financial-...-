
# 📊 Benford's Law Audit Tool

Benford's Law Audit Tool is a Python-based Streamlit application designed to help auditors and analysts detect anomalies in numerical datasets by analyzing the distribution of leading digits according to Benford’s Law.

## 🔍 Features
- **Benford’s Law Analysis**:
  - First Digit (1–9) and First Two Digit (10–99) distribution checks
  - Comparison with theoretical Benford distribution
  - Chi-squared and T-test statistical evaluations

- **Interactive Visualizations**:
  - Bar charts and boxplots for digit distribution and variance
  - Filterable data tables for suspicious transactions

- **Suspicious Transaction Detection**:
  - Automatic identification of digits with > ±5% variance
  - Value range filtering for targeted review

- **Automated Audit Insights**:
  - Auto-detection of numeric columns
  - Handles missing and zero values
  - Provides audit recommendations based on statistical results

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/benford-audit-tool.git
   ```
2. Navigate to the project folder:
   ```bash
   cd benford-audit-tool
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage
Run the Streamlit app:
```bash
streamlit run app.py
```
Then open the provided local URL in your browser to use the tool.

## 📁 File Formats Supported
- CSV (.csv)
- Excel (.xlsx)

## 📄 License
This project is licensed under the MIT License.
