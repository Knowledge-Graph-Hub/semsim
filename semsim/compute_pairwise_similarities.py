"""Compute pairwise similarities."""

import pathlib
from itertools import combinations
from typing import Dict

from grape import Graph
from grape.similarities import DAGResnik


def compute_pairwise_sims(
    dag: Graph,
    counts: Dict[str, int],
    cutoff: float,
    prefixes: list,
    path: str,
    root_node: str,
) -> bool:
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
    root_node: str
        Name of a root node to specify for Jaccard comparisons.
    return: bool
        True if successful
    """
    print(
        f"Calculating Resnik and Jaccard scores for {', '.join(prefixes)}..."
    )

    dag_name = dag.get_name()
    outpath = pathlib.Path.cwd() / path
    rs_path = outpath / f"{dag_name}_similarities"

    resnik_model = DAGResnik()
    resnik_model.fit(dag, node_counts=counts)

    if root_node != "":
        root_select = [dag.get_node_id_from_node_name(root_node)]
        print(f"Will use single root as specified: {root_node}")
    else:
        all_roots = dag.get_root_node_ids()
        if len(all_roots) == 1:
            root_select = [dag.get_root_node_ids()[0]]
            root_name = dag.get_node_name_from_node_id(root_select[0])
            print(f"Found single root: {root_name}")
        else:
            root_select = dag.get_root_node_ids()
            root_names = dag.get_node_names_from_node_ids(root_select)
            print(f"Found multiple roots: {root_names}")

    # Get all similarities,
    # based on the provided prefixes and cutoff.
    try:

        print("Computing Resnik...")
        rs_df = resnik_model.get_similarities_from_clique_graph_node_prefixes(
            node_prefixes=prefixes,
            minimum_similarity=cutoff,
            return_similarities_dataframe=True,
        )

        print("Computing Jaccard...")
        all_jaccard_names = []
        for root in root_select:
            root_name = dag.get_node_name_from_node_id(root)
            if len(root_select) == 1:
                jaccard_name = "jaccard"
            else:
                jaccard_name = f"jaccard_{root_name}"
                all_jaccard_names.append(jaccard_name)
            rs_df[jaccard_name] = dag.get_ancestors_jaccard_from_node_ids(
                dag.get_breadth_first_search_from_node_ids(
                    src_node_id=root,
                    compute_predecessors=True,
                ),
                list(rs_df["source"]),
                list(rs_df["destination"]),
            )

        if len(root_select) > 1:
            print("Determining maximum Jaccard similarity...")
            rs_df["jaccard"] = rs_df[all_jaccard_names].max(axis=1)

        # Remap node IDs to node names
        print("Retrieving node names...")
        for col in ["source", "destination"]:
            rs_df[col] = dag.get_node_names_from_node_ids(rs_df[col])

        print(f"Writing output to {rs_path}...")
        rs_df.sort_values(by=["resnik_score"], ascending=False, inplace=True)

        rs_df.to_csv(rs_path, index=False)

        success = True
    except ValueError as e:
        print(e)
        success = False

    return success


def compute_subset_sims(
    dag: Graph,
    counts: Dict[str, int],
    nodes: list,
) -> dict:
    """Compute Resnik and Jaccard similarities for a given list of nodes.

    Parameters
    -------------------
    dag: Graph
        The DAG to use to compute the Resnik and Jaccard similarities.
    counts: Dict[str, int]
        The counts to use for Resnik similarity.
    nodes: list
        Nodes to be will be compared for similarity.
    return: dict of tuples, with the IDs of each pair (a tuple) as
    the key and a tuple of (Resnik, Jaccard) as value.
    """
    print(f"Calculating Resnik and Jaccard scores for {len(nodes)} nodes...")

    all_sims = {}
    all_pairs = combinations(nodes, 2)

    resnik_model = DAGResnik()
    resnik_model.fit(dag, node_counts=counts)

    for pair in all_pairs:
        rs = resnik_model.get_similarities_from_bipartite_graph_node_names(
            source_node_names=pair[0], destination_node_names=pair[1]
        )
        rs_lst = list(rs[0].flat)
        if len(rs_lst) == 0:
            rs_val = 0
        else:
            rs_val = rs_lst[0]

        js = dag.get_ancestors_jaccard_from_node_names(
            dag.get_breadth_first_search_from_node_names(
                src_node_name=dag.get_root_node_names()[0],
                compute_predecessors=True,
            ),
            [pair[0]],
            [pair[1]],
        )
        all_sims[pair] = (float(rs_val), float(js))

    return all_sims
