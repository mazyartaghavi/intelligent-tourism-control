# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

**Citation:** Patrick Lewis et al. (2020). *Advances in Neural Information Processing Systems*, NeurIPS 2020. Published conference paper. [Author record and persistent identifier](https://arxiv.org/abs/2005.11401).

**Reviewed:** 2026-10-17. [Full-text manuscript](https://arxiv.org/pdf/2005.11401), version 4; abstract and Sections 3-4 on experiments and results.

## Findings

The paper combines a dense retriever over a Wikipedia index with a sequence-to-sequence generator. Sequence-level and token-level variants condition generation on retrieved passages. The experiments cover question answering, question generation, and fact verification, with improvements over selected non-retrieval baselines on reported measures.

## Relevance to This Repository

Our interpretation: use retrieved evidence to support tourism assistance and explain structured recommendations through the [grounded language interface](../../methodology/mathematical-framework.md#6-grounded-language-interface). Keep numerical decisions supplied by the allocation and pricing modules authoritative.

## Limitations

The experiments do not validate current local information or multilingual tourism assistance. Retrieval does not guarantee factual correctness, and this fine-tuned architecture is not identical to every prompt-based retrieval pipeline.

## Proposed Next Step

Compare matched assistants with and without retrieval on a fixed query set, checking evidence support, stale information, abstention, and consistency with structured decisions.
