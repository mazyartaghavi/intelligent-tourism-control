# Parallelizing the dual revised simplex method

**Citation:** Q. Huangfu and J. A. J. Hall (2018 issue; first online 2017). *Mathematical Programming Computation*, 10, 119–142. Published journal article. [Publisher full text; DOI: 10.1007/s12532-017-0130-5](https://link.springer.com/article/10.1007/s12532-017-0130-5).

**Reviewed:** 2026-11-09. Full-text Sections 2.1–2.2, 5.2–5.4, and 6.

## Findings

The dual revised simplex method seeks primal feasibility while maintaining dual feasibility. The paper compares parallelism across iterations through suboptimization (PAMI) with overlapping work within an iteration (SIP). Computational results show complementary behavior across sparse LP problems; extra work and coordination can outweigh parallel gains.

## Relevance to This Repository

Our interpretation: the [allocation model](../../research/optimization-milestone.md#deterministic-allocation-formulation) should use an established sparse LP solver and report numerical diagnostics. The repository's solver integration calls SciPy's HiGHS dual-simplex backend; it does not implement the paper's parallel algorithms. The [HiGHS project](https://highs.dev/) identifies this article as its recommended citation.

## Limitations

Historical solver benchmarks do not predict runtime on small allocation instances, current library versions, or different hardware. Parallel speedup is distinct from better allocation decisions. Preprocessing, sparsity, and iteration counts affect comparisons.

## Proposed Next Step

Scale the allocation horizon and location count while holding scenario generation fixed. Compare preprocessing settings, recording model size, construction time, solve time, objective agreement, and primal-dual residuals. Repeat timings after warm-up and preserve all failures. This performance study is proposed, separate from the current decision-quality benchmark.
