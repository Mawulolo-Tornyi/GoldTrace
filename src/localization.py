from __future__ import annotations


def estimate_zone(node_a_abnormal:bool,node_b_abnormal:bool)->str:
    if not node_a_abnormal and node_b_abnormal: return "BETWEEN_NODE_A_AND_NODE_B"
    if node_a_abnormal and node_b_abnormal: return "UPSTREAM_OF_NODE_A_OR_WIDESPREAD_EVENT"
    if node_a_abnormal and not node_b_abnormal: return "NODE_A_LOCAL_ANOMALY"
    return "NO_SUSPECTED_ZONE"
