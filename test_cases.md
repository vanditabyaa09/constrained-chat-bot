# Test Cases for PDF Conversational Agent

## Overview
This document provides comprehensive test cases for validating the PDF Q&A system using a sample research paper or policy document. Tests cover valid queries, out-of-scope rejection, citation accuracy, and relevance thresholding.

---

## Sample PDF Reference
**Recommended test documents:**
- Research paper: arXiv PDF (e.g., "Attention is All You Need", "BERT: Pre-training of Deep Bidirectional Transformers")
- Policy document: Government white papers, technical specifications
- Technical report: Industry standards or technical documentation

**Requirements:** Multi-page document (8+ pages) with:
- Clear sections and subsections
- At least one table or figure
- Defined introduction and conclusion
- Specific page references for validation

---

## Part 1: VALID QUERIES (Expected Success)

### Test Case 1.1: Factual Question (Specific Page)

**Query:**
```
"What is the main contribution of this paper?"
```

**Expected Behavior:**
✅ **SUCCESS**
- Retriever finds highly relevant chunks (similarity score ≥ 0.45)
- LLM provides answer directly from abstract/introduction
- Response includes specific page citation [Page 1] or [Page 2]

**Example Expected Output:**
```
"The main contribution of this paper is the introduction of the Transformer 
architecture, which relies entirely on attention mechanisms without any recurrence 
or convolution. This approach achieves state-of-the-art results on sequence-to-sequence 
tasks while being more parallelizable. [Page 1]"
```

**Validation Checklist:**
- [ ] Response appears within 3-5 seconds
- [ ] Contains factual information from document
- [ ] Ends with page citation [Page X]
- [ ] Check terminal logs: `Best score: 0.72 >= 0.45 ✓ RELEVANT`

---

### Test Case 1.2: Summary Question (Multi-Section)

**Query:**
```
"Summarize the methodology used in this research"
```

**Expected Behavior:**
✅ **SUCCESS**
- Retriever returns top-5 chunks from multiple sections (e.g., pages 2-4)
- LLM synthesizes information across chunks
- Response cites multiple pages if information spans them

**Example Expected Output:**
```
"The methodology involves three key components: (1) The encoder-decoder architecture 
with multi-head attention, detailed in Section 3. (2) Training on the WMT dataset 
with label smoothing, as described in Section 4. (3) Extensive ablation studies 
to validate each component. [Page 3, Page 4]"
```

**Validation Checklist:**
- [ ] Response integrates information from multiple pages
- [ ] Logical flow between sections
- [ ] Multiple citations present (e.g., [Page 3], [Page 4])
- [ ] Terminal shows top-5 chunks from different page numbers

---

### Test Case 1.3: Follow-up Question (Conversation History)

**Query Sequence:**
```
1. First query: "What are the experimental results on the BLEU metric?"
   → Expected: Agent retrieves results section with specific scores

2. Follow-up: "How does this compare to the previous state-of-the-art?"
   → Expected: Agent uses conversation history to understand context
```

**Expected Behavior:**
✅ **SUCCESS**
- Agent maintains conversation history (last 4 turns)
- Second query reuses context from first answer
- Avoids redundant retrieval if context already sufficient

**Example Expected Output (Query 2):**
```
"Based on the results presented earlier, the Transformer model achieves 
28.4 BLEU on English-to-German translation, which represents a 2.0 point 
improvement over the previous best result of 26.4 BLEU. This improvement 
is attributed to the more efficient attention mechanism. [Page 5]"
```

**Validation Checklist:**
- [ ] Follow-up doesn't require re-explaining first query
- [ ] Natural conversational flow
- [ ] Agent references previous context
- [ ] Terminal logs show history context included in prompt

---

### Test Case 1.4: Question About Table/Figure

**Query:**
```
"What does Table 2 show about the model performance?"
```

**Expected Behavior:**
✅ **SUCCESS**
- Retriever finds chunks containing table descriptions or data
- LLM interprets table content (or extracts from surrounding text)
- Response references the specific table and cites the page

**Example Expected Output:**
```
"Table 2 presents a detailed breakdown of the Transformer model's performance 
on different datasets. The model achieves 28.4 BLEU on WMT14 En-De, 
24.6 BLEU on WMT14 En-Fr, and shows consistent improvements over baseline 
models across all metrics. The table also demonstrates that the attention 
mechanism is the key factor in performance gains. [Page 5]"
```

**Validation Checklist:**
- [ ] Response directly addresses table content
- [ ] Specific numerical values from table are mentioned
- [ ] Table location cited [Page X]
- [ ] Terminal shows retrieved chunks include table page

---

### Test Case 1.5: Conclusion Question

**Query:**
```
"What are the main conclusions and future work mentioned in the paper?"
```

**Expected Behavior:**
✅ **SUCCESS**
- Retriever finds conclusion section (typically last 1-2 pages)
- LLM summarizes key takeaways and next steps
- Response includes citations to conclusion pages

**Example Expected Output:**
```
"The paper concludes that attention-based architectures without recurrence 
or convolution are more efficient and achieve superior results on machine translation 
tasks. Future work includes exploring attention mechanisms for other tasks like 
image recognition, investigating ways to reduce the computational cost of 
attention, and exploring ways to handle longer sequences more efficiently. [Page 12]"
```

**Validation Checklist:**
- [ ] Response references conclusion/future work sections
- [ ] Forward-looking statements present
- [ ] Cites last pages of document
- [ ] Terminal shows chunks from end of document

---

## Part 2: OUT-OF-SCOPE QUERIES (Expected Rejection)

### Test Case 2.1: General Knowledge Question

**Query:**
```
"What is machine learning?"
```

**Expected Behavior:**
❌ **REJECTED (Scope Guard Triggered)**
- Retriever finds weak semantic matches (similarity score < 0.45)
- Agent recognizes out-of-scope
- Returns polite refusal

**Expected Output:**
```
"I can only answer questions based on the uploaded PDF. This question appears 
to be outside its scope."
```

**Verification Steps:**
1. Check terminal logs:
   ```
   [Retrieval] Top-1 score: 0.32
   [Scope Guard] Best score: 0.32 < 0.45 ✗ OUT-OF-SCOPE → REJECTED
   ```
2. Confirm refusal message appears (not an LLM-generated answer)
3. Verify LLM was never called (no "Mistral generation" log)

**Validation Checklist:**
- [ ] Refusal message appears immediately (< 1 second)
- [ ] No "LLM generation" or "Calling Mistral" in logs
- [ ] Best score clearly shown as < 0.45 in logs
- [ ] User sees consistent refusal message

---

### Test Case 2.2: Topic Never Mentioned in PDF

**Query:**
```
"What does this paper say about blockchain technology?"
```

**Expected Behavior:**
❌ **REJECTED (Scope Guard Triggered)**
- Retriever has no relevant chunks for "blockchain"
- Best similarity score drops below threshold
- Scope guard prevents hallucination attempt

**Expected Output:**
```
"I can only answer questions based on the uploaded PDF. This question appears 
to be outside its scope."
```

**Verification Steps:**
1. Check terminal logs for very low scores:
   ```
   [Retrieval] Top-5 scores: [0.28, 0.25, 0.22, 0.18, 0.15]
   [Scope Guard] Best score: 0.28 < 0.45 ✗ OUT-OF-SCOPE → REJECTED
   ```
2. Confirm no partial answers are generated
3. Verify threshold check prevents LLM from guessing

**Validation Checklist:**
- [ ] All top-5 scores below 0.45
- [ ] Immediate rejection (no LLM processing)
- [ ] Consistent refusal across multiple queries
- [ ] No mention of "blockchain" in response

---

### Test Case 2.3: Request for Out-of-Domain Task

**Query:**
```
"Write Python code to implement the Transformer model"
```

**Expected Behavior:**
❌ **REJECTED**
- Query contains words from PDF (Transformer, model) but intent is different
- Similarity score may be moderate (~0.45-0.55) due to keyword overlap
- System prompt explicitly forbids task generation
- Response refuses to generate code

**Expected Output (System Prompt Enforcement):**
```
"I can only answer questions about the content of the uploaded PDF. 
I cannot write code or perform tasks outside of answering questions about 
the document. If you'd like to know about the Transformer architecture 
as described in the paper, I'd be happy to explain that instead."
```

**Verification Steps:**
1. Check if score is above 0.45 but LLM still refuses
2. Verify system prompt worked (not retrieval guard)
3. Logs show:
   ```
   [Retrieval] Best score: 0.52 >= 0.45 ✓ RELEVANT
   [LLM Generation] Using system prompt: "Answer ONLY using the context..."
   [Output] Refused code generation (system prompt enforcement)
   ```

**Validation Checklist:**
- [ ] No Python code in response
- [ ] Refusal message specific to task generation
- [ ] Offers alternative (answering about Transformer in PDF)
- [ ] System prompt logged as enforced

---

## Part 3: Verification Methods

### 3.1 Verify Scope Guard is Working

**Steps:**

1. **Launch the agent with debug logging:**
   ```bash
   python main.py
   # Terminal should show detailed logs
   ```

2. **Submit an out-of-scope query:**
   ```
   "Tell me about quantum computing"
   ```

3. **Check terminal output for:**
   ```
   [Query Embedding] Generated embedding for: "Tell me about quantum computing"
   [Retrieval] Searching top-5 chunks...
   [Retrieval Results]:
     Chunk 1 (Page 2): score=0.31
     Chunk 2 (Page 4): score=0.29
     Chunk 3 (Page 1): score=0.27
     Chunk 4 (Page 5): score=0.25
     Chunk 5 (Page 3): score=0.22
   [Scope Guard] Best score: 0.31 < 0.45 ✗ OUT-OF-SCOPE
   [Output] Rejection message sent (no LLM call)
   ```

4. **Verify response does NOT:**
   - Contain made-up information about quantum computing
   - Have any page citations
   - Show LLM generation time
   - Reference information outside the PDF

---

### 3.2 Verify Citations are Accurate

**Steps:**

1. **Collect a response with citations:**
   ```
   Query: "What is the key innovation?"
   Response: "The paper introduces self-attention mechanisms for sequence processing... [Page 3]"
   ```

2. **Manually verify the citation:**
   - Open the original PDF
   - Navigate to Page 3
   - Search for "self-attention" or related terms
   - Confirm the text/concept appears on that page

3. **Check multiple citations:**
   - Run 5-10 valid queries
   - For each response with citations, verify 1-2 page numbers manually
   - Create a verification table:

   | Query | Cited Page | Concept | Manual Verification | Status |
   |-------|-----------|---------|-------------------|--------|
   | "What is attention?" | 3 | Self-attention mechanism | Found on page 3 ✓ | PASS |
   | "Describe training" | 5 | Training procedure | Found on page 5-6 ✓ | PASS |
   | "What are results?" | 8 | BLEU scores | Found on page 8 ✓ | PASS |

4. **Validation Criteria:**
   - ✅ Cited page contains concept/data mentioned
   - ✅ Information is within ±1 page of correct location
   - ✅ No citations to pages before introduction or after conclusion
   - ❌ If citations are completely wrong, investigate:
     - Retriever returned wrong chunks
     - LLM hallucinated a page number
     - Metadata loss in pipeline

---

### 3.3 Verify Retrieval Quality

**Steps:**

1. **Add debug output to agent.py** (optional):
   ```python
   def chat(self, query: str, history: list = None) -> str:
       # ... existing code ...
       retrieved_chunks = self.retriever.retrieve(query_embedding, top_k=5)
       
       # DEBUG: Print chunk details
       for i, chunk in enumerate(retrieved_chunks):
           print(f"[DEBUG] Chunk {i+1}:")
           print(f"  Page: {chunk['metadata']['page']}")
           print(f"  Score: {chunk['similarity_score']:.3f}")
           print(f"  Text preview: {chunk['text'][:100]}...")
   ```

2. **For a valid query, observe:**
   - Top chunk has score ≥ 0.6 (high relevance)
   - Chunks are from expected pages (e.g., introduction for "main topic")
   - Text preview contains query keywords

3. **For an out-of-scope query, observe:**
   - Top chunk has score < 0.45
   - Retrieved text has weak semantic overlap
   - Keywords may match but meaning is different

---

## Part 4: Threshold Tuning Tests

### 4.1 Lower Threshold (0.3) — More Permissive

**Setup:**
```python
# In app/agent.py line 17
RELEVANCE_THRESHOLD = 0.3
```

**Test Query:**
```
"What is this paper about?" (ambiguous, general)
```

**Expected:**
- More weak matches pass the guard
- Fewer out-of-scope rejections
- Risk: More hallucinations or irrelevant answers

**Action:** Monitor for:
- [ ] More queries accepted
- [ ] More responses with lower confidence
- [ ] Potential for mixing information from weak matches

---

### 4.2 Higher Threshold (0.7) — More Strict

**Setup:**
```python
# In app/agent.py line 17
RELEVANCE_THRESHOLD = 0.7
```

**Test Query:**
```
"What is this paper about?"
```

**Expected:**
- Only strong matches pass
- More rejections even for reasonable queries
- Better safety but reduced usability

**Action:** Monitor for:
- [ ] More rejections of valid queries
- [ ] More conservative/short answers
- [ ] Better specificity in accepted answers

---

## Part 5: End-to-End Test Workflow

### Complete Test Session

```bash
# 1. Start the agent
cd /path/to/ai-chat-bot
python main.py
# → Opens http://localhost:7860

# 2. Upload test PDF
# → Status: "✓ PDF loaded: paper.pdf, 127 chunks indexed"

# 3. Run Valid Query Test (1.1)
Query: "What is the main contribution of this paper?"
Expected: ✅ Specific answer with [Page X]
Result: PASS / FAIL

# 4. Run Out-of-Scope Test (2.1)
Query: "What is machine learning?"
Expected: ❌ Rejection message
Result: PASS / FAIL
Terminal Check: Best score < 0.45? ✓

# 5. Run Follow-up Test (1.3)
Query 1: "What are the experimental results?"
Query 2: "How does this compare to baselines?"
Expected: ✅ Both answered with context awareness
Result: PASS / FAIL

# 6. Verify Citations (Part 3.2)
Sample 3 responses, check page numbers manually
Result: X/3 citations verified accurate

# 7. Document Results
Success Rate: 5/8 tests passed
Issues Found: [list any failures]
Threshold Setting: 0.45
Recommendation: [adjust threshold if needed]
```

---

## Part 6: Common Test Failures & Debugging

| Failure Mode | Cause | Debug Steps |
|---|---|---|
| Citation to wrong page | Chunking boundaries lose context | Check `PDFProcessor.CHUNK_SIZE` and overlap |
| Acceptance of out-of-scope query | Threshold too low | Increase `RELEVANCE_THRESHOLD` to 0.5 |
| Rejection of valid query | Threshold too high | Decrease to 0.35, check embedding quality |
| No response (timeout) | LLM API rate limit | Wait 60s, check HF free tier usage |
| Repeated generic answers | Retriever always finds same chunks | Verify embeddings are normalized |
| Hallucinated citations | LLM generating fake page numbers | Strengthen system prompt, add citation validation |

---

## Recommended Test Execution Checklist

- [ ] Test Case 1.1: Factual question on single page
- [ ] Test Case 1.2: Summary spanning multiple sections
- [ ] Test Case 1.3: Follow-up question with history
- [ ] Test Case 1.4: Question about table/figure
- [ ] Test Case 1.5: Conclusion question
- [ ] Test Case 2.1: General knowledge rejection
- [ ] Test Case 2.2: Unmentioned topic rejection
- [ ] Test Case 2.3: Task request rejection
- [ ] Verify scope guard (Part 3.1)
- [ ] Verify citations (Part 3.2)
- [ ] Verify retrieval (Part 3.3)
- [ ] Threshold tuning (Part 4)
- [ ] Document pass/fail rates
- [ ] Identify any remaining edge cases

---

## Success Criteria

✅ **System passes if:**
- Valid queries return cited answers (5/5 tests pass)
- Out-of-scope queries are rejected (3/3 tests pass)
- Citations are accurate (manual spot-check: ≥80% correct)
- Scope guard rejects with scores < 0.45
- System prompt prevents code generation
- Follow-up questions use conversation history
- No hallucinations in final test sweep

❌ **System needs fixes if:**
- Any valid query returns refusal
- Any out-of-scope query passes through
- Citations point to wrong pages
- Scope guard score doesn't match behavior
- LLM generates outside-scope information
