# 🧪 Testability & Validation Guide

This document fulfills the internship assignment requirement for providing a testable environment with specific evaluation criteria.

## 📂 Sample PDF
- **File Name**: `test.pdf` (located in the project root)
- **Document Type**: Research Paper ("Attention is All You Need")

---

## ✅ Part 1: Valid Queries (In-Scope)
Use these queries to verify the RAG pipeline, retrieval accuracy, and citation engine.

| # | Query | Expected Behavior | Expected Citation |
| :--- | :--- | :--- | :--- |
| 1 | "What is the main contribution of this paper?" | Agent should describe the Transformer architecture and its reliance on attention. | [Page 1] or [Page 2] |
| 2 | "Explain the Multi-Head Attention mechanism." | Detailed breakdown of the attention layers and their parallel nature. | [Page 4] or [Page 5] |
| 3 | "What datasets were used for the English-to-German translation task?" | References to the WMT 2014 English-German dataset. | [Page 7] |
| 4 | "Summarize the experimental results on the BLEU metric." | Should list scores like 28.4 for EN-DE and 41.8 for EN-FR. | [Page 7] or [Page 8] |
| 5 | "What is the conclusion of the research?" | Summary of how the model achieves state-of-the-art with less training. | [Page 10] |

---

## ❌ Part 2: Invalid Queries (Out-of-Scope)
Use these queries to verify the **Scope Guard** and hallucination prevention.

| # | Query | Expected Behavior | Rationale |
| :--- | :--- | :--- | :--- |
| 1 | "What is the recipe for chocolate cake?" | **Refusal**: "I can only answer questions based on the uploaded PDF..." | Similarity score will be < 0.45. |
| 2 | "Who won the World Cup in 2022?" | **Refusal**: "I can only answer questions based on the uploaded PDF..." | Topic not present in the document. |
| 3 | "Can you write a Python script for a snake game?" | **Refusal**: "I can only answer questions based on the uploaded PDF..." | Request is for a task outside the document's domain. |

---

## 🛠️ Validation Criteria
To confirm the bot is working effectively, check the following during your demo:

1.  **Relevance Score**: Open your terminal. For valid queries, you should see `Best score: 0.XX >= 0.45`. For invalid queries, you should see `Best score: 0.XX < 0.45`.
2.  **Citation Accuracy**: Verify that the page number in the citation pill [Page X] actually contains the text mentioned in the AI's answer.
3.  **No Hallucinations**: Ensure the bot does not use external knowledge (like GPT-4's training data) to answer the "Out-of-Scope" questions.
