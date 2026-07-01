# RentHub AI - Final Evaluation Report

This report summarizes the performance metrics of the RentHub AI system components based on the executed Jupyter Notebook.

## 1. Intent Detection (Llama-3.1-8B-Instant)
- **Total Test Queries:** 110
- **Overall Accuracy:** 80.91%
- **Macro F1-Score:** 0.72

### Details per Intent Class:
| Intent | F1-Score |
|---|---|
| book_cancel | 0.63 |
| book_confirm | 0.71 |
| book_continue | 0.74 |
| book_initiate | 0.96 |
| filter | 0.33 |
| greet | 0.91 |
| out_of_scope | 0.00 |
| platform_question | 0.96 |
| question | 0.95 |
| recommend | 0.75 |
| search | 0.75 |
| view_orders | 1.00 |


## 2. Entity Extraction Performance
- **Total Test Queries:** 60

| Field | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| name_keyword | 85.00% | - | - | - |
| brand | 80.00% | - | - | - |
| location | 75.00% | - | - | - |
| max_price | 100.00% | - | - | - |
| condition | 100.00% | - | - | - |
| category | 100.00% | - | - | - |

*Note: Detailed Precision/Recall per field is available in the plotted charts.* 

## 3. Booking Agent
*Metrics are currently being generated in the background.*

## 4. Response Generation
*Metrics are currently being generated in the background.*
