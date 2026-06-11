# Nature-inspired-algorithm-for-the-bin-packing-problem
implemented a genetic algorithms (GAs) approach in Python to solving the bin packing problem

The bin-packing problem (BPP) involves n items, each with its own weight. Each item must be placed in one of b bins. The task is to find a way of placing the items into the bins in such a way as to make the total weight in each bin as nearly equal as possible. E.g., if there are 6 items with weights as follows: (17, 12, 19, 6, 4, 28) and we place them into 3 bins as follows indexing from 1:

(bin1: 1, 3) (bin2: 4) (bin3: 2, 5, 6)

then bin1 has weight 36 (17+19), bin2 has weight 6, and bin3 has weight 44 (12+4+28). These are quite different, so it is a poor solution. We can measure the solution quality by taking the difference d between the heaviest and lightest bins – in this case d = 38. What we want to do here is to minimise this difference. A far better solution in this case is: 

(bin1: 1, 2) (bin2: 3, 4, 5) (bin3: 6)

with d = 1. 

You will need to create a chromosome representation to represent the problem. This should be a data structure which contains the bin assignment for each item. For instance, a problem with k items and b bins will be represented as an array of length k, where each gene specifies which bin the corresponding item is assigned to.

Example chromosome for 6 items and 3 bins: [2, 3, 1, 2, 2, 3] This means: item 1 → bin 2, item 2 → bin 3, item 3 → bin 1, item 4 → bin 2, item 5 → bin 2, item 6 → bin 3.

The fitness of a chromosome is worked out by calculating the difference d between the heaviest and 
lightest bins, where the goal is to minimize this difference. There are two specific bin-packing problems I want you to address. In each, there are 500 items to be packed into a number of (b) bins (either 10 or 50). In problem BPP1, b = 10 and the weight of item i (where i starts at 1 and finishes at 500) is i. In problem BPP2, b = 50 and the weight of item i is (i²)/2.
