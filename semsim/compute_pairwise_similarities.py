from typing import Dict
import pandas as pd
from grape.similarities import DAGResnik
from grape import Graph


def compute_pairwise_resnik(dag: Graph, counts: Dict[str, int], path: str):
    """Compute and store pairwise Resnik of the provided graph at given path.

    Parameters
    -------------------
    dag: Graph
        The DAG to use to compute the Resnik similarity.
    counts: Dict[str, int]
        The counts to use for Resnik similarity.
    path: str
        The path where to store the pairwise similarity.
    """
    model = DAGResnik()
    model.fit(
        dag,
        node_counts=counts
    )
    model.get_pairwise_similarities(
        graph=dag,
        return_similarities_dataframe=True
    ).to_csv(path, index=True, header=True)


def compute_pairwise_ancestors_jaccard(dag: Graph, path: str):
    """Compute and store pairwise Ancestors Jaccard of the provided graph at given path.

    Parameters
    -------------------
    dag: Graph
        The DAG to use to compute the Ancestors Jaccard similarity.
    path: str
        The path where to store the pairwise similarity.
    """
    pd.DataFrame(
        dag.get_shared_ancestors_jaccard_adjacency_matrix(
            dag.get_breadth_first_search_from_node_names(
                src_node_name=dag.get_root_node_names()[0],
                compute_predecessors=True
            ),
            verbose=True
        ),
        columns=dag.get_node_names(),
        index=dag.get_node_names()
    ).to_csv(path, index=True, header=True)
