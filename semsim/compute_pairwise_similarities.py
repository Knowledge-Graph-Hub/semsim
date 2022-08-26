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
    print("Calculating pairwise Resnik scores...")

    dag_name = dag.get_name()
    outpath = pathlib.Path.cwd() / path
    rs_path = outpath / f"{dag_name}_resnik"
    rs_path_temp = outpath / f"{dag_name}_resnik_temp"
    js_path = outpath / f"{dag_name}_jaccard"
    paths = [rs_path, js_path]

    nodes_of_interest = [
        node
        for node in dag.get_node_names()
        if (node.split(":"))[0] in prefixes
    ]

    resnik_model = DAGResnik()
    resnik_model.fit(dag, node_counts=counts)

    # Get all pairwise similarities
    # Write to temp file for caching purposes
    # (i.e., so we don't run out of memory)
    try:
        resnik_model.get_pairwise_similarities(
            graph=dag, return_similarities_dataframe=True
        ).to_csv(
            rs_path_temp, index=True, header=True, columns=nodes_of_interest
        )
    except ValueError as e:
        print(e)

    # Now load the file iteratively and filter
    iter_rs_df = pd.read_csv(
        rs_path_temp, iterator=True, index_col=0, chunksize=1
    )
    pd.concat(
        [
            chunk.mask(chunk < cutoff)
            for chunk in iter_rs_df
            if chunk.index in nodes_of_interest
        ]
    ).to_csv(rs_path, index=nodes_of_interest, header=True)

    print("Calculating pairwise Jaccard scores...")
    js_df = pd.DataFrame(
        dag.get_shared_ancestors_jaccard_adjacency_matrix(
            dag.get_breadth_first_search_from_node_names(
                src_node_name=dag.get_root_node_names()[0],
                compute_predecessors=True,
            ),
            verbose=True,
        ),
        columns=dag.get_node_names(),
        index=dag.get_node_names(),
    )
    js_df.drop(
        columns=[col for col in js_df if col not in nodes_of_interest],
        inplace=True,
    )
    js_df.drop(
        index=[idx for idx in js_df.index if idx not in nodes_of_interest],
        inplace=True,
    )
    js_df.to_csv(js_path, index=True, header=True)

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
