# Main results at the default cell (n=5 owners, pooled over 3 partitions x 3 seeds)

## webqsp

### Comparison arms (under the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.869 | 0.940 | 5.96 | 1.40 | 6.51 | 424 | 0.235 | 1.43 |
| Broadcast-all | 0.967 | 0.957 | 7.78 | 1.43 | 8.06 | 554 | 0.556 | 1.43 |
| Star coordinator | 0.967 | 0.957 | 7.78 | 1.43 | 8.06 | 554 | 0.556 | 1.43 |
| Random gossip | 0.953 | 0.957 | 5.11 | 1.43 | 8.06 | 356 | 0.533 | 1.43 |
| Distributed semijoin | 0.967 | 0.957 | 6.89 | 1.43 | 8.06 | 481 | 0.550 | 1.43 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.609 | 0.667 | 134.08 | 31.03 | 128.95 | 10669 | 1.514 | 1.36 |
| Budgeted 3-agent (CLAUSE-style) | 0.965 | 0.956 | 7.67 | 1.43 | 8.04 | 546 | 0.556 | 1.43 |
| Value suppression (AskSafely-style) | 0.967 | 0.957 | 6.89 | 1.43 | 7.35 | 481 | 0.550 | 1.43 |
| DECENT (B=4) | 0.721 | 0.806 | 0.08 | 0.08 | 2.85 | 6 | 0.007 | 1.27 |
| DECENT (unbudgeted) | 0.953 | 0.957 | 0.52 | 0.40 | 7.38 | 37 | 0.096 | 1.43 |
| DECENT, raw certificates | 0.953 | 0.957 | 5.11 | 1.43 | 8.06 | 356 | 0.532 | 1.43 |

### Ceilings (reference only; these break the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Union | 0.967 | 0.957 | 4354.16 | 295.72 | 1427.38 | 344965 | 2.116 | 1.43 |
| Exact centralised join | 0.967 | 0.957 | 7.78 | 1.43 | 8.06 | 554 | 0.000 | 1.43 |

### Stratified by owners spanned (comparison arms)

**1 owner(s) spanned, 1616 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.984 | 0.979 | 5.09 | 1.12 | 5.98 | 363 | 0.000 | 1.12 |
| Broadcast-all | 0.984 | 0.979 | 5.09 | 1.12 | 5.98 | 363 | 0.000 | 1.12 |
| Star coordinator | 0.984 | 0.979 | 5.09 | 1.12 | 5.98 | 363 | 0.000 | 1.12 |
| Random gossip | 0.970 | 0.978 | 3.84 | 1.12 | 5.98 | 270 | 0.000 | 1.12 |
| Distributed semijoin | 0.984 | 0.979 | 5.04 | 1.12 | 5.98 | 360 | 0.000 | 1.12 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.547 | 0.600 | 117.59 | 27.40 | 115.55 | 9441 | 1.231 | 1.09 |
| Budgeted 3-agent (CLAUSE-style) | 0.984 | 0.979 | 5.09 | 1.12 | 5.98 | 363 | 0.000 | 1.12 |
| Value suppression (AskSafely-style) | 0.984 | 0.979 | 5.04 | 1.12 | 5.94 | 360 | 0.000 | 1.12 |
| DECENT (B=4) | 0.861 | 0.946 | 0.10 | 0.10 | 2.36 | 7 | 0.000 | 1.09 |
| DECENT (unbudgeted) | 0.970 | 0.978 | 0.37 | 0.28 | 5.25 | 26 | 0.000 | 1.12 |
| DECENT, raw certificates | 0.970 | 0.978 | 3.84 | 1.12 | 5.98 | 270 | 0.000 | 1.12 |

**2 owner(s) spanned, 504 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.860 | 0.919 | 8.10 | 1.90 | 7.69 | 578 | 0.667 | 1.92 |
| Broadcast-all | 0.941 | 0.926 | 8.47 | 1.91 | 8.01 | 606 | 0.920 | 1.92 |
| Star coordinator | 0.941 | 0.926 | 8.47 | 1.91 | 8.01 | 606 | 0.920 | 1.92 |
| Random gossip | 0.938 | 0.926 | 5.12 | 1.91 | 8.01 | 353 | 0.944 | 1.92 |
| Distributed semijoin | 0.941 | 0.926 | 6.67 | 1.91 | 8.01 | 452 | 0.943 | 1.92 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.710 | 0.730 | 129.97 | 32.50 | 122.98 | 10197 | 1.812 | 1.75 |
| Budgeted 3-agent (CLAUSE-style) | 0.935 | 0.922 | 8.21 | 1.91 | 7.97 | 586 | 0.919 | 1.92 |
| Value suppression (AskSafely-style) | 0.941 | 0.926 | 6.67 | 1.91 | 6.63 | 452 | 0.943 | 1.92 |
| DECENT (B=4) | 0.642 | 0.668 | 0.11 | 0.10 | 3.19 | 8 | 0.040 | 1.63 |
| DECENT (unbudgeted) | 0.938 | 0.926 | 0.59 | 0.47 | 7.34 | 42 | 0.183 | 1.92 |
| DECENT, raw certificates | 0.938 | 0.926 | 5.12 | 1.91 | 8.01 | 353 | 0.942 | 1.92 |

**3 owner(s) spanned, 237 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.691 | 0.888 | 5.33 | 1.86 | 5.60 | 361 | 0.595 | 1.92 |
| Broadcast-all | 0.952 | 0.938 | 7.12 | 1.93 | 7.14 | 491 | 1.456 | 1.94 |
| Star coordinator | 0.952 | 0.938 | 7.12 | 1.93 | 7.14 | 491 | 1.456 | 1.94 |
| Random gossip | 0.952 | 0.938 | 4.78 | 1.93 | 7.14 | 338 | 1.379 | 1.94 |
| Distributed semijoin | 0.952 | 0.938 | 5.72 | 1.93 | 7.14 | 399 | 1.425 | 1.94 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.711 | 0.784 | 166.43 | 37.97 | 157.17 | 13144 | 1.959 | 1.79 |
| Budgeted 3-agent (CLAUSE-style) | 0.952 | 0.938 | 7.12 | 1.93 | 7.14 | 491 | 1.456 | 1.94 |
| Value suppression (AskSafely-style) | 0.952 | 0.938 | 5.72 | 1.93 | 5.78 | 399 | 1.425 | 1.94 |
| DECENT (B=4) | 0.592 | 0.650 | 0.04 | 0.04 | 3.77 | 3 | 0.000 | 1.61 |
| DECENT (unbudgeted) | 0.952 | 0.938 | 0.51 | 0.49 | 6.45 | 36 | 0.165 | 1.94 |
| DECENT, raw certificates | 0.952 | 0.938 | 4.78 | 1.93 | 7.14 | 338 | 1.375 | 1.94 |

**4 owner(s) spanned, 148 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.544 | 0.821 | 5.69 | 1.74 | 5.96 | 436 | 0.473 | 1.86 |
| Broadcast-all | 0.941 | 0.920 | 10.32 | 1.88 | 9.55 | 753 | 1.823 | 1.90 |
| Star coordinator | 0.941 | 0.920 | 10.32 | 1.88 | 9.55 | 753 | 1.823 | 1.90 |
| Random gossip | 0.940 | 0.920 | 6.45 | 1.88 | 9.55 | 435 | 1.640 | 1.90 |
| Distributed semijoin | 0.941 | 0.920 | 7.50 | 1.88 | 9.55 | 510 | 1.749 | 1.90 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.677 | 0.769 | 166.39 | 39.02 | 156.26 | 13342 | 2.042 | 1.78 |
| Budgeted 3-agent (CLAUSE-style) | 0.932 | 0.913 | 9.93 | 1.88 | 9.54 | 723 | 1.816 | 1.90 |
| Value suppression (AskSafely-style) | 0.941 | 0.920 | 7.50 | 1.88 | 7.47 | 510 | 1.749 | 1.90 |
| DECENT (B=4) | 0.408 | 0.554 | 0.00 | 0.00 | 3.97 | 0 | 0.000 | 1.49 |
| DECENT (unbudgeted) | 0.940 | 0.920 | 0.61 | 0.51 | 8.95 | 40 | 0.184 | 1.90 |
| DECENT, raw certificates | 0.940 | 0.920 | 6.45 | 1.88 | 9.55 | 434 | 1.637 | 1.90 |

**5 owner(s) spanned, 195 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.407 | 0.822 | 8.67 | 1.67 | 9.39 | 595 | 0.445 | 1.77 |
| Broadcast-all | 0.938 | 0.916 | 27.24 | 1.77 | 25.40 | 1924 | 2.173 | 1.79 |
| Star coordinator | 0.938 | 0.916 | 27.24 | 1.77 | 25.40 | 1924 | 2.173 | 1.79 |
| Random gossip | 0.866 | 0.913 | 15.05 | 1.77 | 25.40 | 1042 | 2.022 | 1.79 |
| Distributed semijoin | 0.938 | 0.916 | 23.74 | 1.77 | 25.40 | 1634 | 2.124 | 1.79 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.686 | 0.837 | 217.52 | 42.88 | 200.38 | 17027 | 2.155 | 1.74 |
| Budgeted 3-agent (CLAUSE-style) | 0.927 | 0.908 | 26.64 | 1.77 | 25.23 | 1881 | 2.173 | 1.79 |
| Value suppression (AskSafely-style) | 0.938 | 0.916 | 23.74 | 1.77 | 22.70 | 1634 | 2.124 | 1.79 |
| DECENT (B=4) | 0.152 | 0.393 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 1.15 |
| DECENT (unbudgeted) | 0.866 | 0.913 | 1.53 | 1.02 | 25.09 | 109 | 0.517 | 1.79 |
| DECENT, raw certificates | 0.866 | 0.913 | 15.06 | 1.77 | 25.40 | 1043 | 2.016 | 1.79 |


## cwq

### Comparison arms (under the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.842 | 0.868 | 5.67 | 1.93 | 6.26 | 435 | 0.486 | 1.98 |
| Broadcast-all | 0.930 | 0.924 | 7.18 | 2.01 | 7.52 | 552 | 0.709 | 2.01 |
| Star coordinator | 0.930 | 0.924 | 7.18 | 2.01 | 7.52 | 552 | 0.709 | 2.01 |
| Random gossip | 0.930 | 0.924 | 3.32 | 2.01 | 7.52 | 249 | 0.693 | 2.01 |
| Distributed semijoin | 0.930 | 0.924 | 3.82 | 2.01 | 7.52 | 290 | 0.705 | 2.01 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.623 | 0.643 | 135.30 | 32.09 | 123.93 | 10585 | 1.555 | 1.88 |
| Budgeted 3-agent (CLAUSE-style) | 0.930 | 0.924 | 7.18 | 2.01 | 7.52 | 551 | 0.709 | 2.01 |
| Value suppression (AskSafely-style) | 0.930 | 0.924 | 3.82 | 2.01 | 4.31 | 290 | 0.705 | 2.01 |
| DECENT (B=4) | 0.644 | 0.685 | 0.06 | 0.06 | 2.88 | 5 | 0.013 | 1.65 |
| DECENT (unbudgeted) | 0.930 | 0.924 | 0.44 | 0.39 | 6.76 | 33 | 0.125 | 2.01 |
| DECENT, raw certificates | 0.930 | 0.924 | 3.32 | 2.01 | 7.52 | 249 | 0.692 | 2.01 |

### Ceilings (reference only; these break the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Union | 0.930 | 0.924 | 3872.49 | 270.91 | 1343.62 | 304678 | 2.113 | 2.01 |
| Exact centralised join | 0.930 | 0.924 | 7.18 | 2.01 | 7.52 | 552 | 0.000 | 2.01 |

### Stratified by owners spanned (comparison arms)

**1 owner(s) spanned, 1016 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.963 | 0.959 | 2.93 | 1.47 | 3.80 | 224 | 0.000 | 1.47 |
| Broadcast-all | 0.963 | 0.959 | 2.93 | 1.47 | 3.80 | 224 | 0.000 | 1.47 |
| Star coordinator | 0.963 | 0.959 | 2.93 | 1.47 | 3.80 | 224 | 0.000 | 1.47 |
| Random gossip | 0.963 | 0.959 | 2.22 | 1.47 | 3.80 | 165 | 0.000 | 1.47 |
| Distributed semijoin | 0.963 | 0.959 | 2.30 | 1.47 | 3.80 | 171 | 0.000 | 1.47 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.727 | 0.743 | 64.78 | 20.99 | 62.41 | 5079 | 1.020 | 1.42 |
| Budgeted 3-agent (CLAUSE-style) | 0.963 | 0.959 | 2.93 | 1.47 | 3.80 | 224 | 0.000 | 1.47 |
| Value suppression (AskSafely-style) | 0.963 | 0.959 | 2.30 | 1.47 | 3.17 | 171 | 0.000 | 1.47 |
| DECENT (B=4) | 0.872 | 0.898 | 0.10 | 0.10 | 2.00 | 8 | 0.000 | 1.40 |
| DECENT (unbudgeted) | 0.963 | 0.959 | 0.29 | 0.26 | 3.01 | 22 | 0.000 | 1.47 |
| DECENT, raw certificates | 0.963 | 0.959 | 2.22 | 1.47 | 3.80 | 165 | 0.000 | 1.47 |

**2 owner(s) spanned, 1072 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.902 | 0.915 | 7.08 | 2.19 | 7.54 | 546 | 0.795 | 2.21 |
| Broadcast-all | 0.921 | 0.923 | 7.20 | 2.20 | 7.61 | 556 | 0.825 | 2.21 |
| Star coordinator | 0.921 | 0.923 | 7.20 | 2.20 | 7.61 | 556 | 0.825 | 2.21 |
| Random gossip | 0.921 | 0.923 | 3.57 | 2.20 | 7.61 | 267 | 0.898 | 2.21 |
| Distributed semijoin | 0.921 | 0.923 | 3.97 | 2.20 | 7.61 | 299 | 0.900 | 2.21 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.548 | 0.567 | 152.92 | 34.30 | 141.09 | 11997 | 1.736 | 2.05 |
| Budgeted 3-agent (CLAUSE-style) | 0.921 | 0.923 | 7.20 | 2.20 | 7.61 | 555 | 0.825 | 2.21 |
| Value suppression (AskSafely-style) | 0.921 | 0.923 | 3.97 | 2.20 | 4.53 | 299 | 0.900 | 2.21 |
| DECENT (B=4) | 0.640 | 0.694 | 0.06 | 0.06 | 3.13 | 4 | 0.032 | 1.88 |
| DECENT (unbudgeted) | 0.921 | 0.923 | 0.48 | 0.42 | 6.85 | 36 | 0.181 | 2.21 |
| DECENT, raw certificates | 0.921 | 0.923 | 3.57 | 2.20 | 7.61 | 267 | 0.898 | 2.21 |

**3 owner(s) spanned, 308 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.681 | 0.769 | 9.53 | 2.42 | 9.63 | 722 | 0.888 | 2.50 |
| Broadcast-all | 0.878 | 0.850 | 10.76 | 2.53 | 10.66 | 812 | 1.319 | 2.53 |
| Star coordinator | 0.878 | 0.850 | 10.76 | 2.53 | 10.66 | 812 | 1.319 | 2.53 |
| Random gossip | 0.878 | 0.850 | 4.06 | 2.53 | 10.66 | 305 | 1.441 | 2.53 |
| Distributed semijoin | 0.878 | 0.850 | 4.85 | 2.53 | 10.66 | 372 | 1.462 | 2.53 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.592 | 0.601 | 195.39 | 44.22 | 178.59 | 15100 | 2.011 | 2.30 |
| Budgeted 3-agent (CLAUSE-style) | 0.878 | 0.850 | 10.75 | 2.53 | 10.66 | 811 | 1.319 | 2.53 |
| Value suppression (AskSafely-style) | 0.878 | 0.850 | 4.85 | 2.53 | 4.90 | 372 | 1.462 | 2.53 |
| DECENT (B=4) | 0.401 | 0.413 | 0.00 | 0.00 | 3.81 | 0 | 0.000 | 1.81 |
| DECENT (unbudgeted) | 0.878 | 0.850 | 0.46 | 0.44 | 9.91 | 34 | 0.193 | 2.53 |
| DECENT, raw certificates | 0.878 | 0.850 | 4.06 | 2.53 | 10.66 | 305 | 1.441 | 2.53 |

**4 owner(s) spanned, 129 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.516 | 0.664 | 4.55 | 2.14 | 5.30 | 363 | 0.735 | 2.36 |
| Broadcast-all | 0.886 | 0.864 | 9.17 | 2.45 | 8.89 | 715 | 1.860 | 2.45 |
| Star coordinator | 0.886 | 0.864 | 9.17 | 2.45 | 8.89 | 715 | 1.860 | 2.45 |
| Random gossip | 0.886 | 0.864 | 5.13 | 2.45 | 8.89 | 382 | 1.517 | 2.45 |
| Distributed semijoin | 0.886 | 0.864 | 6.30 | 2.45 | 8.89 | 481 | 1.610 | 2.45 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.634 | 0.680 | 208.45 | 46.09 | 191.67 | 16839 | 2.210 | 2.32 |
| Budgeted 3-agent (CLAUSE-style) | 0.886 | 0.864 | 9.16 | 2.45 | 8.89 | 714 | 1.860 | 2.45 |
| Value suppression (AskSafely-style) | 0.886 | 0.864 | 6.30 | 2.45 | 6.19 | 481 | 1.610 | 2.45 |
| DECENT (B=4) | 0.279 | 0.357 | 0.00 | 0.00 | 3.96 | 0 | 0.000 | 1.80 |
| DECENT (unbudgeted) | 0.886 | 0.864 | 0.60 | 0.53 | 8.17 | 45 | 0.225 | 2.45 |
| DECENT, raw certificates | 0.886 | 0.864 | 5.14 | 2.45 | 8.89 | 382 | 1.513 | 2.45 |

**5 owner(s) spanned, 175 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.289 | 0.385 | 6.96 | 1.88 | 7.55 | 532 | 0.515 | 2.39 |
| Broadcast-all | 0.913 | 0.910 | 23.98 | 2.66 | 22.11 | 1854 | 2.202 | 2.66 |
| Star coordinator | 0.913 | 0.910 | 23.98 | 2.66 | 22.11 | 1854 | 2.202 | 2.66 |
| Random gossip | 0.913 | 0.910 | 5.55 | 2.66 | 22.11 | 421 | 1.537 | 2.66 |
| Distributed semijoin | 0.913 | 0.910 | 8.15 | 2.66 | 22.11 | 645 | 1.612 | 2.66 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.526 | 0.580 | 277.22 | 51.42 | 229.79 | 21348 | 2.268 | 2.46 |
| Budgeted 3-agent (CLAUSE-style) | 0.913 | 0.910 | 23.93 | 2.66 | 22.11 | 1851 | 2.202 | 2.66 |
| Value suppression (AskSafely-style) | 0.913 | 0.910 | 8.15 | 2.66 | 7.17 | 645 | 1.612 | 2.66 |
| DECENT (B=4) | 0.044 | 0.116 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 1.27 |
| DECENT (unbudgeted) | 0.913 | 0.910 | 0.86 | 0.70 | 21.42 | 64 | 0.319 | 2.66 |
| DECENT, raw certificates | 0.913 | 0.910 | 5.54 | 2.66 | 22.11 | 420 | 1.528 | 2.66 |


## metaqa1hop

### Comparison arms (under the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.949 | 0.975 | 1.88 | 1.00 | 2.88 | 94 | 0.000 | 1.00 |
| Broadcast-all | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |
| Star coordinator | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |
| Random gossip | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |
| Distributed semijoin | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.983 | 0.976 | 8.14 | 4.33 | 8.56 | 395 | 0.878 | 1.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |
| Value suppression (AskSafely-style) | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |
| DECENT (B=4) | 0.951 | 0.977 | 0.11 | 0.11 | 1.79 | 6 | 0.001 | 1.00 |
| DECENT (unbudgeted) | 0.982 | 0.976 | 0.21 | 0.17 | 2.32 | 11 | 0.008 | 1.00 |
| DECENT, raw certificates | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.136 | 1.00 |

### Ceilings (reference only; these break the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Union | 0.982 | 0.976 | 267164.00 | 18.00 | 43234.00 | 13430260 | 2.207 | 1.00 |
| Exact centralised join | 0.982 | 0.976 | 2.15 | 1.00 | 3.15 | 108 | 0.000 | 1.00 |

### Stratified by owners spanned (comparison arms)

**1 owner(s) spanned, 2433 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| Broadcast-all | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| Star coordinator | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| Random gossip | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| Distributed semijoin | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.987 | 0.982 | 7.94 | 4.40 | 8.37 | 384 | 0.783 | 1.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| Value suppression (AskSafely-style) | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |
| DECENT (B=4) | 0.963 | 0.983 | 0.11 | 0.11 | 1.62 | 5 | 0.000 | 1.00 |
| DECENT (unbudgeted) | 0.986 | 0.982 | 0.18 | 0.15 | 2.01 | 9 | 0.000 | 1.00 |
| DECENT, raw certificates | 0.986 | 0.982 | 1.86 | 1.00 | 2.86 | 93 | 0.000 | 1.00 |

**2 owner(s) spanned, 108 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.691 | 0.940 | 1.52 | 1.00 | 2.52 | 78 | 0.000 | 1.00 |
| Broadcast-all | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.958 | 1.00 |
| Star coordinator | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.958 | 1.00 |
| Random gossip | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.959 | 1.00 |
| Distributed semijoin | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.958 | 1.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.970 | 0.954 | 6.61 | 3.52 | 7.06 | 319 | 1.523 | 1.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.958 | 1.00 |
| Value suppression (AskSafely-style) | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.958 | 1.00 |
| DECENT (B=4) | 0.958 | 0.954 | 0.32 | 0.31 | 2.83 | 18 | 0.019 | 1.00 |
| DECENT (unbudgeted) | 0.970 | 0.954 | 0.39 | 0.36 | 2.92 | 21 | 0.028 | 1.00 |
| DECENT, raw certificates | 0.970 | 0.954 | 2.56 | 1.00 | 3.56 | 132 | 0.959 | 1.00 |

**3 owner(s) spanned, 82 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.558 | 0.902 | 1.78 | 1.00 | 2.78 | 90 | 0.000 | 1.00 |
| Broadcast-all | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.521 | 1.00 |
| Star coordinator | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.521 | 1.00 |
| Random gossip | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.524 | 1.00 |
| Distributed semijoin | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.521 | 1.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.937 | 0.917 | 10.20 | 3.93 | 10.62 | 489 | 1.815 | 1.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.521 | 1.00 |
| Value suppression (AskSafely-style) | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.521 | 1.00 |
| DECENT (B=4) | 0.857 | 0.918 | 0.10 | 0.10 | 3.67 | 5 | 0.000 | 1.00 |
| DECENT (unbudgeted) | 0.937 | 0.917 | 0.38 | 0.30 | 4.28 | 20 | 0.055 | 1.00 |
| DECENT, raw certificates | 0.937 | 0.917 | 3.98 | 1.00 | 4.98 | 200 | 1.524 | 1.00 |

**4 owner(s) spanned, 41 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.487 | 0.894 | 2.24 | 1.00 | 3.24 | 107 | 0.000 | 1.00 |
| Broadcast-all | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |
| Star coordinator | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |
| Random gossip | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |
| Distributed semijoin | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.913 | 0.888 | 12.37 | 3.95 | 12.20 | 587 | 2.043 | 1.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |
| Value suppression (AskSafely-style) | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |
| DECENT (B=4) | 0.722 | 0.894 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 1.00 |
| DECENT (unbudgeted) | 0.913 | 0.888 | 0.46 | 0.39 | 6.49 | 21 | 0.063 | 1.00 |
| DECENT, raw certificates | 0.913 | 0.888 | 6.10 | 1.00 | 7.10 | 293 | 1.910 | 1.00 |

**5 owner(s) spanned, 27 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.477 | 0.907 | 4.81 | 1.00 | 5.81 | 256 | 0.000 | 1.00 |
| Broadcast-all | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.169 | 1.00 |
| Star coordinator | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.169 | 1.00 |
| Random gossip | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.173 | 1.00 |
| Distributed semijoin | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.169 | 1.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.909 | 0.890 | 20.00 | 2.85 | 19.52 | 1047 | 2.181 | 1.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.169 | 1.00 |
| Value suppression (AskSafely-style) | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.169 | 1.00 |
| DECENT (B=4) | 0.416 | 0.898 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 1.00 |
| DECENT (unbudgeted) | 0.909 | 0.890 | 1.41 | 0.67 | 15.81 | 77 | 0.447 | 1.00 |
| DECENT, raw certificates | 0.909 | 0.890 | 15.15 | 1.00 | 16.15 | 810 | 2.173 | 1.00 |


## metaqa2hop

### Comparison arms (under the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.828 | 0.888 | 6.48 | 1.99 | 6.79 | 348 | 0.661 | 2.00 |
| Broadcast-all | 0.944 | 0.910 | 8.81 | 2.00 | 8.61 | 473 | 0.953 | 2.00 |
| Star coordinator | 0.944 | 0.910 | 8.81 | 2.00 | 8.61 | 473 | 0.953 | 2.00 |
| Random gossip | 0.944 | 0.910 | 6.86 | 2.00 | 8.61 | 367 | 0.921 | 2.00 |
| Distributed semijoin | 0.944 | 0.910 | 8.25 | 2.00 | 8.61 | 441 | 0.945 | 2.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.936 | 0.907 | 31.36 | 7.21 | 24.50 | 1544 | 1.459 | 2.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.943 | 0.910 | 8.67 | 2.00 | 8.49 | 465 | 0.952 | 2.00 |
| Value suppression (AskSafely-style) | 0.944 | 0.910 | 8.25 | 2.00 | 8.05 | 441 | 0.945 | 2.00 |
| DECENT (B=4) | 0.637 | 0.729 | 0.05 | 0.05 | 3.33 | 3 | 0.018 | 1.87 |
| DECENT (unbudgeted) | 0.944 | 0.910 | 0.81 | 0.50 | 8.06 | 44 | 0.209 | 2.00 |
| DECENT, raw certificates | 0.944 | 0.910 | 6.85 | 2.00 | 8.61 | 367 | 0.907 | 2.00 |

### Ceilings (reference only; these break the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Union | 0.944 | 0.910 | 267164.00 | 18.00 | 43234.00 | 13430260 | 2.207 | 2.00 |
| Exact centralised join | 0.944 | 0.910 | 8.81 | 2.00 | 8.61 | 473 | 0.000 | 2.00 |

### Stratified by owners spanned (comparison arms)

**1 owner(s) spanned, 474 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.947 | 0.915 | 6.24 | 2.00 | 6.62 | 338 | 0.000 | 2.00 |
| Broadcast-all | 0.947 | 0.915 | 6.24 | 2.00 | 6.62 | 338 | 0.000 | 2.00 |
| Star coordinator | 0.947 | 0.915 | 6.24 | 2.00 | 6.62 | 338 | 0.000 | 2.00 |
| Random gossip | 0.947 | 0.915 | 5.48 | 2.00 | 6.62 | 296 | 0.000 | 2.00 |
| Distributed semijoin | 0.947 | 0.915 | 5.93 | 2.00 | 6.62 | 321 | 0.000 | 2.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.943 | 0.915 | 19.10 | 6.91 | 15.84 | 948 | 0.508 | 2.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.946 | 0.915 | 6.08 | 2.00 | 6.47 | 329 | 0.000 | 2.00 |
| Value suppression (AskSafely-style) | 0.947 | 0.915 | 5.93 | 2.00 | 6.31 | 321 | 0.000 | 2.00 |
| DECENT (B=4) | 0.778 | 0.844 | 0.11 | 0.11 | 3.05 | 5 | 0.000 | 1.95 |
| DECENT (unbudgeted) | 0.947 | 0.915 | 0.70 | 0.45 | 6.03 | 38 | 0.000 | 2.00 |
| DECENT, raw certificates | 0.947 | 0.915 | 5.48 | 2.00 | 6.62 | 296 | 0.000 | 2.00 |

**2 owner(s) spanned, 1490 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.922 | 0.912 | 6.60 | 2.00 | 6.81 | 351 | 0.842 | 2.00 |
| Broadcast-all | 0.947 | 0.916 | 6.83 | 2.00 | 6.96 | 362 | 0.884 | 2.00 |
| Star coordinator | 0.947 | 0.916 | 6.83 | 2.00 | 6.96 | 362 | 0.884 | 2.00 |
| Random gossip | 0.947 | 0.916 | 5.37 | 2.00 | 6.96 | 284 | 0.894 | 2.00 |
| Distributed semijoin | 0.947 | 0.916 | 6.33 | 2.00 | 6.96 | 334 | 0.895 | 2.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.939 | 0.912 | 25.55 | 7.18 | 20.31 | 1250 | 1.487 | 2.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.947 | 0.916 | 6.77 | 2.00 | 6.91 | 359 | 0.884 | 2.00 |
| Value suppression (AskSafely-style) | 0.947 | 0.916 | 6.33 | 2.00 | 6.46 | 334 | 0.895 | 2.00 |
| DECENT (B=4) | 0.710 | 0.785 | 0.06 | 0.06 | 3.16 | 3 | 0.032 | 1.91 |
| DECENT (unbudgeted) | 0.947 | 0.916 | 0.60 | 0.42 | 6.35 | 32 | 0.190 | 2.00 |
| DECENT, raw certificates | 0.947 | 0.916 | 5.37 | 2.00 | 6.96 | 283 | 0.888 | 2.00 |

**3 owner(s) spanned, 290 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.650 | 0.844 | 5.88 | 1.99 | 6.39 | 320 | 0.770 | 2.00 |
| Broadcast-all | 0.925 | 0.881 | 8.63 | 2.00 | 8.43 | 464 | 1.432 | 2.00 |
| Star coordinator | 0.925 | 0.881 | 8.63 | 2.00 | 8.43 | 464 | 1.432 | 2.00 |
| Random gossip | 0.925 | 0.881 | 6.85 | 2.00 | 8.43 | 368 | 1.344 | 2.00 |
| Distributed semijoin | 0.925 | 0.881 | 8.19 | 2.00 | 8.43 | 438 | 1.409 | 2.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.920 | 0.881 | 31.55 | 7.37 | 24.67 | 1563 | 1.888 | 2.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.924 | 0.881 | 8.57 | 2.00 | 8.38 | 460 | 1.432 | 2.00 |
| Value suppression (AskSafely-style) | 0.925 | 0.881 | 8.19 | 2.00 | 7.99 | 438 | 1.409 | 2.00 |
| DECENT (B=4) | 0.574 | 0.667 | 0.00 | 0.00 | 3.73 | 0 | 0.000 | 1.89 |
| DECENT (unbudgeted) | 0.925 | 0.881 | 0.81 | 0.56 | 7.96 | 44 | 0.239 | 2.00 |
| DECENT, raw certificates | 0.925 | 0.881 | 6.82 | 2.00 | 8.43 | 366 | 1.317 | 2.00 |

**4 owner(s) spanned, 177 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.550 | 0.821 | 5.64 | 1.97 | 6.12 | 306 | 0.728 | 2.00 |
| Broadcast-all | 0.933 | 0.887 | 10.69 | 2.00 | 9.67 | 571 | 1.820 | 2.00 |
| Star coordinator | 0.933 | 0.887 | 10.69 | 2.00 | 9.67 | 571 | 1.820 | 2.00 |
| Random gossip | 0.933 | 0.887 | 7.93 | 2.00 | 9.67 | 422 | 1.676 | 2.00 |
| Distributed semijoin | 0.933 | 0.887 | 10.39 | 2.00 | 9.67 | 554 | 1.769 | 2.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.930 | 0.887 | 37.78 | 7.37 | 29.35 | 1864 | 2.097 | 2.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.933 | 0.887 | 10.69 | 2.00 | 9.67 | 571 | 1.820 | 2.00 |
| Value suppression (AskSafely-style) | 0.933 | 0.887 | 10.39 | 2.00 | 9.37 | 554 | 1.769 | 2.00 |
| DECENT (B=4) | 0.372 | 0.527 | 0.00 | 0.00 | 3.99 | 0 | 0.000 | 1.81 |
| DECENT (unbudgeted) | 0.933 | 0.887 | 0.92 | 0.62 | 9.26 | 49 | 0.291 | 2.00 |
| DECENT, raw certificates | 0.933 | 0.887 | 7.89 | 2.00 | 9.67 | 420 | 1.624 | 2.00 |

**5 owner(s) spanned, 215 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.382 | 0.770 | 7.65 | 1.96 | 8.15 | 420 | 0.656 | 2.00 |
| Broadcast-all | 0.950 | 0.912 | 26.89 | 2.00 | 23.75 | 1469 | 2.169 | 2.00 |
| Star coordinator | 0.950 | 0.912 | 26.89 | 2.00 | 23.75 | 1469 | 2.169 | 2.00 |
| Random gossip | 0.950 | 0.912 | 19.34 | 2.00 | 23.75 | 1060 | 1.951 | 2.00 |
| Distributed semijoin | 0.950 | 0.912 | 25.04 | 2.00 | 23.75 | 1365 | 2.072 | 2.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.922 | 0.898 | 93.14 | 7.73 | 68.37 | 4602 | 2.252 | 2.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.945 | 0.912 | 26.04 | 2.00 | 22.98 | 1423 | 2.162 | 2.00 |
| Value suppression (AskSafely-style) | 0.950 | 0.912 | 25.04 | 2.00 | 21.90 | 1365 | 2.072 | 2.00 |
| DECENT (B=4) | 0.123 | 0.332 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 1.47 |
| DECENT (unbudgeted) | 0.950 | 0.912 | 2.45 | 1.05 | 23.53 | 136 | 0.691 | 2.00 |
| DECENT, raw certificates | 0.950 | 0.912 | 19.30 | 2.00 | 23.75 | 1057 | 1.889 | 2.00 |


## metaqa3hop

### Comparison arms (under the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.681 | 0.839 | 24.18 | 2.96 | 21.46 | 1293 | 0.869 | 3.00 |
| Broadcast-all | 0.932 | 0.890 | 39.25 | 3.00 | 32.90 | 2074 | 1.407 | 3.00 |
| Star coordinator | 0.932 | 0.890 | 39.25 | 3.00 | 32.90 | 2074 | 1.407 | 3.00 |
| Random gossip | 0.932 | 0.890 | 23.34 | 3.00 | 32.90 | 1217 | 1.368 | 3.00 |
| Distributed semijoin | 0.932 | 0.890 | 32.86 | 3.00 | 32.90 | 1705 | 1.411 | 3.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.826 | 0.870 | 124.32 | 8.62 | 88.35 | 6169 | 1.834 | 3.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.891 | 0.867 | 33.76 | 2.98 | 28.90 | 1803 | 1.383 | 3.00 |
| Value suppression (AskSafely-style) | 0.932 | 0.890 | 32.86 | 3.00 | 27.05 | 1705 | 1.411 | 3.00 |
| DECENT (B=4) | 0.043 | 0.047 | 0.00 | 0.00 | 3.99 | 0 | 0.000 | 2.15 |
| DECENT (unbudgeted) | 0.932 | 0.890 | 3.28 | 1.39 | 32.90 | 173 | 0.584 | 3.00 |
| DECENT, raw certificates | 0.932 | 0.890 | 23.32 | 3.00 | 32.90 | 1215 | 1.348 | 3.00 |

### Ceilings (reference only; these break the ownership constraint)

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Union | 0.932 | 0.890 | 267164.00 | 18.00 | 43234.00 | 13430260 | 2.207 | 3.00 |
| Exact centralised join | 0.932 | 0.890 | 39.25 | 3.00 | 32.90 | 2074 | 0.000 | 3.00 |

### Stratified by owners spanned (comparison arms)

**1 owner(s) spanned, 79 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.866 | 0.796 | 9.39 | 3.00 | 8.32 | 501 | 0.000 | 3.00 |
| Broadcast-all | 0.866 | 0.796 | 9.39 | 3.00 | 8.32 | 501 | 0.000 | 3.00 |
| Star coordinator | 0.866 | 0.796 | 9.39 | 3.00 | 8.32 | 501 | 0.000 | 3.00 |
| Random gossip | 0.866 | 0.796 | 5.71 | 3.00 | 8.32 | 296 | 0.000 | 3.00 |
| Distributed semijoin | 0.866 | 0.796 | 7.28 | 3.00 | 8.32 | 382 | 0.000 | 3.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.809 | 0.761 | 41.89 | 8.01 | 29.66 | 2102 | 0.207 | 3.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.866 | 0.796 | 9.39 | 3.00 | 8.32 | 501 | 0.000 | 3.00 |
| Value suppression (AskSafely-style) | 0.866 | 0.796 | 7.28 | 3.00 | 6.49 | 382 | 0.000 | 3.00 |
| DECENT (B=4) | 0.184 | 0.203 | 0.00 | 0.00 | 3.97 | 0 | 0.000 | 2.57 |
| DECENT (unbudgeted) | 0.866 | 0.796 | 0.54 | 0.49 | 8.32 | 28 | 0.000 | 3.00 |
| DECENT, raw certificates | 0.866 | 0.796 | 5.71 | 3.00 | 8.32 | 296 | 0.000 | 3.00 |

**2 owner(s) spanned, 710 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.890 | 0.878 | 36.07 | 3.00 | 31.00 | 1922 | 0.734 | 3.00 |
| Broadcast-all | 0.923 | 0.877 | 36.85 | 3.00 | 31.51 | 1960 | 0.800 | 3.00 |
| Star coordinator | 0.923 | 0.877 | 36.85 | 3.00 | 31.51 | 1960 | 0.800 | 3.00 |
| Random gossip | 0.923 | 0.877 | 22.23 | 3.00 | 31.51 | 1164 | 0.849 | 3.00 |
| Distributed semijoin | 0.923 | 0.877 | 30.00 | 3.00 | 31.51 | 1567 | 0.856 | 3.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.789 | 0.847 | 103.09 | 8.51 | 73.61 | 5085 | 1.534 | 3.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.884 | 0.854 | 31.36 | 2.98 | 27.33 | 1689 | 0.781 | 3.00 |
| Value suppression (AskSafely-style) | 0.923 | 0.877 | 30.00 | 3.00 | 25.27 | 1567 | 0.856 | 3.00 |
| DECENT (B=4) | 0.054 | 0.059 | 0.00 | 0.00 | 3.99 | 0 | 0.000 | 2.20 |
| DECENT (unbudgeted) | 0.923 | 0.877 | 3.18 | 1.28 | 31.51 | 168 | 0.378 | 3.00 |
| DECENT, raw certificates | 0.923 | 0.877 | 22.22 | 3.00 | 31.51 | 1164 | 0.841 | 3.00 |

**3 owner(s) spanned, 751 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.841 | 0.858 | 24.45 | 2.99 | 20.59 | 1288 | 1.039 | 3.00 |
| Broadcast-all | 0.919 | 0.871 | 26.81 | 3.00 | 22.09 | 1407 | 1.240 | 3.00 |
| Star coordinator | 0.919 | 0.871 | 26.81 | 3.00 | 22.09 | 1407 | 1.240 | 3.00 |
| Random gossip | 0.919 | 0.871 | 14.27 | 3.00 | 22.09 | 733 | 1.318 | 3.00 |
| Distributed semijoin | 0.919 | 0.871 | 21.41 | 3.00 | 22.09 | 1097 | 1.310 | 3.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.837 | 0.851 | 91.95 | 8.54 | 64.71 | 4565 | 1.763 | 3.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.903 | 0.862 | 25.26 | 2.99 | 21.15 | 1332 | 1.234 | 3.00 |
| Value suppression (AskSafely-style) | 0.919 | 0.871 | 21.41 | 3.00 | 17.19 | 1097 | 1.310 | 3.00 |
| DECENT (B=4) | 0.066 | 0.069 | 0.00 | 0.00 | 3.99 | 0 | 0.000 | 2.24 |
| DECENT (unbudgeted) | 0.919 | 0.871 | 1.92 | 1.14 | 22.09 | 99 | 0.490 | 3.00 |
| DECENT, raw certificates | 0.919 | 0.871 | 14.26 | 3.00 | 22.09 | 732 | 1.304 | 3.00 |

**4 owner(s) spanned, 331 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.570 | 0.766 | 17.54 | 2.90 | 16.29 | 941 | 0.819 | 3.00 |
| Broadcast-all | 0.919 | 0.870 | 28.57 | 3.00 | 23.81 | 1497 | 1.632 | 3.00 |
| Star coordinator | 0.919 | 0.870 | 28.57 | 3.00 | 23.81 | 1497 | 1.632 | 3.00 |
| Random gossip | 0.919 | 0.870 | 17.37 | 3.00 | 23.81 | 898 | 1.497 | 3.00 |
| Distributed semijoin | 0.919 | 0.870 | 24.30 | 3.00 | 23.81 | 1251 | 1.591 | 3.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.852 | 0.860 | 98.92 | 8.47 | 70.13 | 4906 | 1.972 | 3.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.903 | 0.861 | 27.42 | 2.99 | 22.97 | 1438 | 1.626 | 3.00 |
| Value suppression (AskSafely-style) | 0.919 | 0.870 | 24.30 | 3.00 | 20.06 | 1251 | 1.591 | 3.00 |
| DECENT (B=4) | 0.041 | 0.048 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 2.22 |
| DECENT (unbudgeted) | 0.919 | 0.870 | 2.24 | 1.31 | 23.81 | 118 | 0.482 | 3.00 |
| DECENT, raw certificates | 0.919 | 0.870 | 17.32 | 3.00 | 23.81 | 895 | 1.462 | 3.00 |

**5 owner(s) spanned, 829 question-runs**

| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | disc bytes | owner entropy | rounds |
|---|---|---|---|---|---|---|---|---|
| Single-Broker | 0.385 | 0.823 | 17.82 | 2.91 | 17.38 | 973 | 0.933 | 3.00 |
| Broadcast-all | 0.963 | 0.936 | 59.69 | 3.00 | 49.86 | 3156 | 2.125 | 3.00 |
| Star coordinator | 0.963 | 0.936 | 59.69 | 3.00 | 49.86 | 3156 | 2.125 | 3.00 |
| Random gossip | 0.963 | 0.936 | 36.57 | 3.00 | 49.86 | 1915 | 1.937 | 3.00 |
| Distributed semijoin | 0.963 | 0.936 | 51.52 | 3.00 | 49.86 | 2682 | 2.040 | 3.00 |
| Neighbourhood retrieval (SPLIT-RAG-style) | 0.838 | 0.922 | 189.83 | 8.92 | 135.26 | 9440 | 2.256 | 3.00 |
| Budgeted 3-agent (CLAUSE-style) | 0.883 | 0.893 | 48.36 | 2.96 | 41.58 | 2598 | 2.068 | 3.00 |
| Value suppression (AskSafely-style) | 0.963 | 0.936 | 51.52 | 3.00 | 42.27 | 2682 | 2.040 | 3.00 |
| DECENT (B=4) | 0.001 | 0.001 | 0.00 | 0.00 | 4.00 | 0 | 0.000 | 1.97 |
| DECENT (unbudgeted) | 0.963 | 0.936 | 5.26 | 1.83 | 49.86 | 279 | 0.942 | 3.00 |
| DECENT, raw certificates | 0.963 | 0.936 | 36.54 | 3.00 | 49.86 | 1912 | 1.905 | 3.00 |


