"""Compute pairwise similarities."""
from typing import Dict

import pandas as pd
from grape import Graph
from grape.similarities import DAGResnik


def compute_pairwise_sims(
    dag: Graph, 
    counts: Dict[str, int], 
    cutoff: float,
    prefixes: list,
    path: str
) -> str:
    """Compute and store pairwise Resnik of the provided graph at given path.

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
    model = DAGResnik()
    model.fit(dag, node_counts=counts)
    interesting_hits = dict()

    nodes_of_interest = [n for n in dag.get_node_names() if n.startswith("HP") or n.startswith("MP")]

    # for each ontology class A (HP or MP) - settable by user
    #     for each ontology class B (HP or MP)
    for a in nodes_of_interest:
        for b in nodes_of_interest:

            try:
                # call pairwise Resnik on r = A, B
                rs = model.get_similarity_from_node_ids([A], [B])

                if rs > cutoff:
                    # call pairwise Jaccard on r = A, B
                    # put in interesting_hits
                    pass
                # model.get_pairwise_similarities(
                #     graph=dag, return_similarities_dataframe=True
                # ).to_csv(path, index=True, header=True)
            except:
                # probably some weird write error message
                pass

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
