"""Compute pairwise similarities."""

import pathlib
from typing import Dict

import pandas as pd
from grape import Graph
from grape.similarities import DAGResnik


def compute_pairwise_sims(
    dag: Graph,
    counts: Dict[str, int],
    cutoff: float,
    prefixes: list,
    path: str,
) -> str:
    """Compute and store pairwise Resnik and Jaccard similarities.

    Parameters
    -------------------
    dag: Graph
        The DAG to use to compute the Resnik and Jaccard similarities.
    counts: Dict[str, int]
        The counts to use for Resnik similarity.
    path: str
        The directory where to store the pairwise similarity.
    cutoff: float
        Pairs with Resnik similarity below this value will not be retained.
    prefixes: list
        Nodes with one of these prefixes will be compared for similarity.
        If not provided, the comparison will be all vs. all on the DAG.
    return: list
        The list of paths where files were written
    """
    print("Calculating pairwise Resnik scores...")

    resnik_model = DAGResnik()
    resnik_model.fit(dag, node_counts=counts)
    rs_hits = {}
    js_hits = {}

    dag_name = dag.get_name()
    outpath = pathlib.Path.cwd() / path
    rs_path = outpath / f"{dag_name}_resnik"
    js_path = outpath / f"{dag_name}_jaccard"
    paths = [rs_path, js_path]

    nodes_of_interest = [
        node
        for node in dag.get_node_names()
        if (node.split(":"))[0] in prefixes
    ]
    nodes_of_interest_i = dag.get_node_ids_from_node_names(nodes_of_interest)
    nodes_of_interest_j = dag.get_node_ids_from_node_names(nodes_of_interest)

    for node_i in nodes_of_interest_i:
        for node_j in nodes_of_interest_j:
            try:
                # call pairwise Resnik on r = A, B
                rs = resnik_model.get_similarity_from_node_ids(
                    [node_i], [node_j]
                )

                if rs > cutoff:
                    if node_i not in rs_hits:
                        rs_hits[node_i] = {}
                    rs_hits[node_i][node_j] = rs

                    # TODO: call pairwise Jaccard on r = A, B
                    # and save to js_hits

            except ValueError as e:
                print(e)

    rs_hits.to_csv(rs_path, index=True, header=True)
    js_hits.to_csv(js_path, index=True, header=True)

    return paths


def compute_pairwise_ancestors_jaccard(dag: Graph, path: str) -> str:
    """Compute and store pairwise Ancestors Jaccard of graph.

    Parameters
    -------------------
    dag: Graph
        The DAG to use to compute the Ancestors Jaccard similarity.
    path: str
        The path where to store the pairwise similarity.
    return: str
        The path where file was written
    """
    print("Calculating pairwise Jaccard scores...")
    pd.DataFrame(
        dag.get_shared_ancestors_jaccard_adjacency_matrix(
            dag.get_breadth_first_search_from_node_names(
                src_node_name=dag.get_root_node_names()[0],
                compute_predecessors=True,
            ),
            verbose=True,
        ),
        columns=dag.get_node_names(),
        index=dag.get_node_names(),
    ).to_csv(path, index=True, header=True)
    return path
