# RAGAs: Automated Evaluation of Retrieval Augmented Generation

**Citation:** Shahul Es, Jithin James, Luis Espinosa-Anke, and Steven Schockaert (2024). *EACL: System Demonstrations*, pp. 150-158. Published conference paper. [Official record; DOI: 10.18653/v1/2024.eacl-demo.16](https://aclanthology.org/2024.eacl-demo.16/).

**Reviewed:** 2026-10-26. [Published full text](https://aclanthology.org/2024.eacl-demo.16.pdf), Sections 3-5 and 8; Table 4. This note concerns the paper's metrics, not subsequent library revisions.

## Findings

RAGAs uses prompted LLMs and embeddings to assess claim support, answer relevance, and context relevance without reference answers. WikiEval draws questions from 50 Wikipedia pages, with two human annotators. Table 4 reports pairwise agreement with human preferences of 0.95 for faithfulness and 0.70 for context relevance.

## Relevance to This Repository

Our interpretation: these separate diagnostics could extend the [language-evaluation protocol](../../experiments/evaluation-protocol.md#5-recommendation-and-language-evaluation). Check retrieved evidence and generated explanations independently. Faithfulness to stale text does not establish current factual accuracy, and numerical agreement with allocation or pricing outputs needs a separate check. RAGAs is not implemented here.

## Limitations

Scores depend on the evaluator model and prompting; repeated runs can differ. The constructed Wikipedia benchmark does not validate tourism-specific or multilingual judgments. Pairwise preference accuracy is not a calibrated probability that an individual answer is correct.

## Proposed Next Step

Construct paired tourism question-context-answer examples containing supported claims, unsupported claims, irrelevant context, and outdated facts. Compare the paper's metrics with blinded human preferences on a held-out set. Repeat with a second evaluator, recording model versions and prompts. Report agreement and run-to-run variation by error type, alongside separate freshness and numerical-consistency checks.
