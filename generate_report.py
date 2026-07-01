import os
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report

EVAL_DIR = Path("evaluation_results")
REPORT_PATH = EVAL_DIR / "Final_Evaluation_Report.md"

md_content = ["# RentHub AI - Final Evaluation Report\n"]
md_content.append("This report summarizes the performance metrics of the RentHub AI system components based on the executed Jupyter Notebook.\n")

# 1. Intent Detection
intent_path = EVAL_DIR / "intent_metrics.csv"
if intent_path.exists():
    df = pd.read_csv(intent_path)
    acc = accuracy_score(df['expected'], df['predicted'])
    report = classification_report(df['expected'], df['predicted'], zero_division=0, output_dict=True)
    f1 = report['macro avg']['f1-score']
    
    md_content.append("## 1. Intent Detection (Llama-3.1-8B-Instant)")
    md_content.append(f"- **Total Test Queries:** {len(df)}")
    md_content.append(f"- **Overall Accuracy:** {acc:.2%}")
    md_content.append(f"- **Macro F1-Score:** {f1:.2f}\n")
    md_content.append("### Details per Intent Class:")
    md_content.append("| Intent | F1-Score |")
    md_content.append("|---|---|")
    for k, v in report.items():
        if k not in ['accuracy', 'macro avg', 'weighted avg']:
            md_content.append(f"| {k} | {v['f1-score']:.2f} |")
    md_content.append("\n")

# 2. Entity Extraction
entity_path = EVAL_DIR / "entity_metrics.csv"
if entity_path.exists():
    df = pd.read_csv(entity_path)
    fields = ["name_keyword", "brand", "location", "max_price", "condition", "category"]
    
    md_content.append("## 2. Entity Extraction Performance")
    md_content.append(f"- **Total Test Queries:** {len(df)}\n")
    md_content.append("| Field | Accuracy | Precision | Recall | F1-Score |")
    md_content.append("|---|---|---|---|---|")
    
    for f in fields:
        match_col = f"match_{f}"
        if match_col in df.columns:
            acc = df[match_col].mean()
            # Approximation for Markdown report (actual precision/recall calculated in notebook)
            md_content.append(f"| {f} | {acc:.2%} | - | - | - |")
    md_content.append("\n*Note: Detailed Precision/Recall per field is available in the plotted charts.* \n")

# Check for Booking
booking_path = EVAL_DIR / "booking_metrics.csv"
if booking_path.exists():
    df = pd.read_csv(booking_path)
    sr = (df['outcome'] == 'CONFIRMED').mean()
    cr = df['outcome'].isin(['CONFIRMED', 'CANCELLED', 'API_FAIL_CAUGHT']).mean()
    md_content.append("## 3. Booking Agent (State Machine)")
    md_content.append(f"- **Simulated Scenarios:** {len(df)}")
    md_content.append(f"- **Success Rate:** {sr:.2%}")
    md_content.append(f"- **Completion Rate (Handled states):** {cr:.2%}")
    md_content.append(f"- **Average Turns per Booking:** {df['turns'].mean():.1f}\n")
else:
    md_content.append("## 3. Booking Agent\n*Metrics are currently being generated in the background.*\n")

# Check for Response Gen
resp_path = EVAL_DIR / "response_generation_metrics.csv"
if resp_path.exists():
    df = pd.read_csv(resp_path)
    md_content.append("## 4. Response Generation (LLM-as-a-Judge)")
    md_content.append(f"- **Average Quality Score:** {df['avg_score'].mean():.2f} / 5.0")
    md_content.append(f"- **Rule-based Pass Rate:** {df['passed_rules'].mean():.2%}\n")
else:
    md_content.append("## 4. Response Generation\n*Metrics are currently being generated in the background.*\n")

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_content))
    
print("Report generated at", REPORT_PATH)
