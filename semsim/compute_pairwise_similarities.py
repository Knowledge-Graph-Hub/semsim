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
) -> list:
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
    print(f"Calculating Resnik scores for {', '.join(prefixes)}...")

    dag_name = dag.get_name()
    outpath = pathlib.Path.cwd() / path
    rs_path = outpath / f"{dag_name}_resnik"
    js_path = outpath / f"{dag_name}_jaccard"
    paths = [rs_path, js_path]

    resnik_model = DAGResnik()
    resnik_model.fit(dag, node_counts=counts)

    # Get all similarities,
    # based on the provided prefixes and cutoff.
    try:
        rs_df = resnik_model. \
            get_similarities_from_bipartite_graph_from_edge_node_prefixes(
                source_node_prefixes=prefixes,
                destination_node_prefixes=prefixes,
                minimum_similarity=cutoff,
                return_similarities_dataframe=True,
            )

        bfs = dag.get_breadth_first_search_from_node_names(
            src_node_name=dag.get_root_node_names()[0],
            compute_predecessors=True,
        )
        rs_df["jaccard"] = dag.get_ancestors_jaccard_from_node_names(
            bfs, list(rs_df["source"]), list(rs_df["destination"])
        )

        rs_df.sort_values(by=["similarity"], ascending=False, inplace=True)

        print("Writing output...")
        rs_df.to_csv(rs_path, index=False)
    except ValueError as e:
        print(e)

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
