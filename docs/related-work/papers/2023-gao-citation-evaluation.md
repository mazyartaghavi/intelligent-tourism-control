# Enabling Large Language Models to Generate Text with Citations

**Citation:** Tianyu Gao, Howard Yen, Jiatong Yu, and Danqi Chen (2023). *EMNLP*, pp. 6465-6488. Published conference paper. [Official record and DOI: 10.18653/v1/2023.emnlp-main.398](https://aclanthology.org/2023.emnlp-main.398/).

**Reviewed:** 2026-11-17. [Published full text](https://aclanthology.org/2023.emnlp-main.398.pdf), Sections 2-3, 5.3, 6, and Limitations; Tables 8-9.

## Findings

ALCE separates fluency, answer correctness, and citation quality across ASQA, QAMPARI, and ELI5. An inference model checks whether cited passages jointly support each statement and whether individual citations are irrelevant. Human and automated evaluations give consistent system rankings in Tables 8-9, while reranking by the automated score produces larger score discrepancies. Citation coverage alone therefore cannot replace answer-quality evaluation.

## Relevance to This Repository

Our interpretation: the [grounded language interface](../../methodology/mathematical-framework.md#6-grounded-language-interface) could require traceable support for tourism claims, alongside the existing [RAGAs review](2024-es-ragas-evaluation.md). Check citation coverage separately from correct reproduction of structured allocation and pricing outputs. ALCE is not implemented here.

## Limitations

The inference model can misjudge support, especially partial support. Benchmark tasks do not establish performance on mathematical reasoning or current tourism information. A citation may faithfully support a claim while the source itself is outdated; freshness needs independent validation.

## Proposed Next Step

Create a held-out tourism question set with dated passages and fixed numerical decisions. Compare citation prompting with post-hoc citation attachment using the same generator and retrieval pool. Include unsupported claims, irrelevant citations, stale opening hours, and altered capacity values. Report human-checked citation precision/recall, answer completeness, freshness errors, and numerical consistency separately. This experiment is proposed.
