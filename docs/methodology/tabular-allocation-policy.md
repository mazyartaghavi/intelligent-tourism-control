# Stage D — Tabular allocation policy

One daily action changes the allocation used to calculate the next day's adjustment cost. This gives a learned policy a reason to consider future cost. The experiment asks whether switching among a small menu of feasible actions improves realized cost on unseen trajectories. Receding-horizon optimization uses point forecasts and models adjustment explicitly. The learned policy has a chance to respond to repeated forecast errors through its training outcomes.

The [daily environment](daily-capacity-control.md) has four candidate actions. The Q table uses five features available before the decision. They encode weekend status, eligible demand relative to budget (cutoffs 1 and 1.4), the size of the change to the priority candidate relative to budget (cutoffs 0.1 and 0.3), whether that candidate raises the highest-penalty site's allocation by more than 10% of budget, and whether tomorrow's forecast load rises by more than 10% of today's budget or tomorrow lies outside the horizon. There are at most 108 feature combinations. Distinct full observations can share a key, so the table represents an approximate state.

For learning rate $\alpha$ and discount $\gamma$, update:

$$
Q(s,a) \leftarrow Q(s,a)+\alpha[r+\gamma\max_{a'}Q(s',a')-Q(s,a)].
$$

The continuation term is zero after the terminal outcome. The published evaluation uses the same undiscounted realized objective for every policy. The discount is a training parameter.

```text
For each learning seed:
    Initialize the Q table and visit counts
    For each pass:
        Shuffle the training scenarios
        For each scenario:
            Reset to zero committed capacity
            For each day:
                Form the key from the public observation
                Choose a random candidate with probability epsilon
                Otherwise choose the best visited candidate or use priority as a fallback
                Commit the feasible allocation and observe the reward
                Update Q and its visit count
    Freeze the policy for evaluation
```

Learning rates, exploration decay, and data partitions are fixed in the [configuration](../../configs/control/stage-e.json). Unseen keys fall back to priority allocation. A four-candidate menu and coarse state allow a bounded local run. They also limit what a negative result can say about other policies or richer states.
