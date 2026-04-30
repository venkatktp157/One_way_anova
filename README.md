# ⚓ Vessel Performance ANOVA Analyzer

This application performs a **One-Way ANOVA** and various **Post-hoc tests** (Tukey, Bonferroni, etc.) to compare the performance metrics (like speed or fuel consumption) across 3 to 10 different vessels.

## 🚀 Features
- **Manual Data Entry**: Input speeds for up to 10 vessels.
- **Bulk Upload**: Supports `.csv` and `.xlsx` files.
- **Statistical Rigor**: Calculates F-Ratio, P-values, and ANOVA tables.
- **Post-hoc Analysis**: Identifies exactly which vessels differ from each other.
- **AI Insights**: Integrated with **Groq LLM** to provide operational inferences.

## 🛠️ Setup Instructions

1. **Clone the repository** (or create the folder).
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

---

### Final Checklist
*   **The .env file**: Make sure the variable name in your `.env` matches the code: `os.getenv("GROQ_API_KEY")`.
*   **Data Consistency**: ANOVA assumes your data is normally distributed and has similar variance. If one vessel has 50 logs and another has only 5, the results may be biased—try to use equal sample sizes for the best results.

### sample data:
Vessel_A,Vessel_B,Vessel_C
14.5,14.2,13.1
14.7,14.1,12.9

vessel-anova-app/
├── .env                # Stores your GROQ_API_KEY (DO NOT SHARE)
├── .gitignore          # Prevents sensitive files from being uploaded to Git
├── app.py              # The main Streamlit application code
├── requirements.txt    # List of Python libraries needed
└── README.md           # Documentation for the project