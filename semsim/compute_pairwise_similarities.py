"""Compute pairwise similarities."""

import pathlib
from typing import Dict

import numpy as np
import pandas as pd
from grape import Graph
from grape.similarities import DAGResnik


def compute_pairwise_sims(
    dag: Graph,
    counts: Dict[str, int],
    cutoff: float,
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
    return: list
        The list of paths where files were written
    """
    print("Calculating pairwise Resnik scores...")

    dag_name = dag.get_name()
    outpath = pathlib.Path.cwd() / path
    rs_path = outpath / f"{dag_name}_resnik"
    js_path = outpath / f"{dag_name}_jaccard"
    paths = [rs_path, js_path]

    resnik_model = DAGResnik()
    resnik_model.fit(dag, node_counts=counts)

    # Get all pairwise similarities
    # This is converted to Sparse as we expect
    # most of the similarities to be below
    # a cutoff value.
    try:
        rs_df = resnik_model.get_pairwise_similarities(
            graph=dag, return_similarities_dataframe=True
        )
        rs_df.mask(rs_df < cutoff, inplace=True)
        rs_df.dropna(axis=0, how="all", inplace=True)
        rs_df = rs_df.astype(pd.SparseDtype("float", np.nan))

        # The following line reshapes the rs_df to a DataFrame with 3 columns:
        # => ['index', 'node_2', 'resnik']
        # Next step would be calculating the Jaccard
        # ('get_ancestors_jaccard_from_node_names')
        # between columns 'index' and 'node_2'
        # rs_df_melted = (
        #     rs_df.reset_index()
        #     .melt(id_vars="index", var_name="node_2", value_name="resnik")
        #     .dropna(axis=0)
        # )
        # OR use stack as suggested by Justin:
        # (https://github.com/Knowledge-Graph-Hub/semsim/pull/4#issuecomment-1234574676)
        rs_df_stacked = (
            rs_df.stack()
            .to_frame()
            .reset_index()
            .rename(
                columns={"level_0": "node_1", "level_1": "node_2", 0: "resnik"}
            )
        )
        # print(rs_df_melted)
        print(rs_df_stacked)
        bfs = dag.get_breadth_first_search_from_node_names(
            src_node_name=dag.get_root_node_names()[0],
            compute_predecessors=True,
        )
        rs_df_stacked["jaccard"] = dag.get_ancestors_jaccard_from_node_names(
            bfs, list(rs_df_stacked["node_1"]), list(rs_df_stacked["node_2"])
        )

        print("Writing output...")
        rs_df_stacked.to_csv(rs_path, index=False)
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
