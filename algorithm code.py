from itertools import combinations

class FPNode:
    """Node in an FP-tree."""
    def __init__(self, item, count, parent):
        self.item = item          # item name
        self.count = count        # item frequency count
        self.parent = parent      # parent node
        self.children = {}        # children node
        self.node_link = None     # next node with the same item

    def increment(self, count=1):
        self.count += count

# Build the FP-tree
def build_fp_tree(transactions, min_sup):
    item_counts = {}
    for trans in transactions:
        for item in trans:
            item_counts[item] = item_counts.get(item, 0) + 1
    freq_items = {i: c for i, c in item_counts.items() if c >= min_sup}

    if not freq_items:
        return None, {}
    order = sorted(freq_items.keys(), key=lambda i: (-freq_items[i], i))
    order_index = {item: idx for idx, item in enumerate(order)}
    header_table = {
        i: {"support": freq_items[i], "head": None}
        for i in order
    }
    root = FPNode(item=None, count=0, parent=None)

    # Insert a single transaction into the FP-tree
    def insert_transaction(node, items, count=1):
        if not items:
            return
        first = items[0]

        if first in node.children:
            child = node.children[first]
            child.increment(count)
        else:
            child = FPNode(first, count, node)
            node.children[first] = child
            head = header_table[first]["head"]
            if head is None:
                header_table[first]["head"] = child
            else:
                while head.node_link is not None:
                    head = head.node_link
                head.node_link = child
        insert_transaction(child, items[1:], count)

    for trans in transactions:
        filtered = [i for i in trans if i in freq_items]
        if not filtered:
            continue
        ordered = sorted(filtered, key=lambda i: order_index[i])
        insert_transaction(root, ordered, count=1)
    return root, header_table

# Check if the FP-tree has a single path
def has_single_path(node):
    children = list(node.children.values())
    if not children:
        return True
    if len(children) > 1:
        return False
    return has_single_path(children[0])

# Traverse a single-path FP-tree and return a list of (item, count)
def get_single_path_items(node):
    path = []
    current = node
    while True:
        children = list(current.children.values())
        if len(children) != 1:
            break
        child = children[0]
        path.append((child.item, child.count))
        current = child
    return path

# Build the conditional pattern for a given item
def conditional_pattern(item, header_table):
    base = []
    node = header_table[item]["head"]
    while node is not None:
        path = []
        parent = node.parent
        while parent is not None and parent.item is not None:
            path.append(parent.item)
            parent = parent.parent
        if path:
            base.append((list(reversed(path)), node.count))
        node = node.node_link
    return base

# Build the conditional FP-tree
def build_conditional_fp_tree(conditional_pattern_base, min_sup):
    item_counts = {}
    for path, count in conditional_pattern_base:
        for item in path:
            item_counts[item] = item_counts.get(item, 0) + count
    freq_items = {i: c for i, c in item_counts.items() if c >= min_sup}
    if not freq_items:
        return None, {}
    order = sorted(freq_items.keys(), key=lambda i: (-freq_items[i], i))
    order_index = {item: idx for idx, item in enumerate(order)}
    header_table = {
        i: {"support": freq_items[i], "head": None}
        for i in order
    }
    root = FPNode(item=None, count=0, parent=None)

    # Insert a weighted path
    def insert_path(node, items, count):
        if not items:
            return
        first = items[0]
        if first in node.children:
            child = node.children[first]
            child.increment(count)
        else:
            child = FPNode(first, count, node)
            node.children[first] = child
            head = header_table[first]["head"]
            if head is None:
                header_table[first]["head"] = child
            else:
                while head.node_link is not None:
                    head = head.node_link
                head.node_link = child
        insert_path(child, items[1:], count)

    # Insert a weighted prefix path into the conditional FP-tree
    for path, count in conditional_pattern_base:
        filtered = [i for i in path if i in freq_items]
        if not filtered:
            continue
        ordered = sorted(filtered, key=lambda i: order_index[i])
        insert_path(root, ordered, count)
    return root, header_table

# Mine the FP-tree
def fp_growth_from_tree(root, header_table, prefix, min_sup, freq_itemsets):
    if not header_table:
        return
    if has_single_path(root):
        path = get_single_path_items(root)
        items = [item for item, cnt in path]
        counts = [cnt for item, cnt in path]
        n = len(items)
        for r in range(1, n + 1):
            for comb_indices in combinations(range(n), r):
                new_itemset = prefix.union(items[i] for i in comb_indices)
                support = min(counts[i] for i in comb_indices)
                freq_itemsets[new_itemset] = freq_itemsets.get(new_itemset, 0) + support
        return

    # Process items in ascending order of frequency
    items = sorted(header_table.keys(), key=lambda i: header_table[i]["support"])
    for item in items:
        new_prefix = prefix.union({item})
        support = header_table[item]["support"]
        freq_itemsets[new_prefix] = freq_itemsets.get(new_prefix, 0) + support
        cond_base = conditional_pattern(item, header_table)
        cond_root, cond_header = build_conditional_fp_tree(cond_base, min_sup)
        if cond_root is not None and cond_header:
            fp_growth_from_tree(cond_root, cond_header, new_prefix, min_sup, freq_itemsets)

# Main FP-Growth
def fp_growth(transactions, min_sup):
    root, header_table = build_fp_tree(transactions, min_sup)
    if root is None:
        return {}
    freq_itemsets = {}
    fp_growth_from_tree(root, header_table, prefix=frozenset(), min_sup=min_sup, freq_itemsets=freq_itemsets)
    return freq_itemsets

# Example usage
if __name__ == "__main__":
    transactions = [
        ['f', 'a', 'c', 'd', 'g', 'i', 'm', 'p'],
        ['a', 'b', 'c', 'f', 'l', 'm', 'o'],
        ['b', 'f', 'h', 'j', 'o'],
        ['b', 'c', 'k', 's', 'p'],
        ['a', 'f', 'c', 'e', 'l', 'p', 'm', 'n'],
    ]

    min_support = 3
    patterns = fp_growth(transactions, min_support)
    
    print("Frequent itemsets (min_sup = 3):")
    for itemset, sup in sorted(patterns.items(), key=lambda x: (-x[1], sorted(list(x[0])))):
        print(list(itemset), ":", sup)