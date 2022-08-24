"""Process ontology and retrieve pairwise similarities."""
import sys
import warnings
from collections import Counter

import pandas as pd

from .compute_pairwise_similarities import compute_pairwise_sims

GRAPE_DATA_MOD = "grape.datasets.kgobo"


def get_similarities(
    ontology: str,
    cutoff: float,
    annot_file: str,
    annot_col: str,
    output_dir: str,
    prefixes: list,
    predicate: str,
) -> bool:
    """Compute and store similarities to the provided paths.

    :param ontology: str, name of ontology to retrieve and process.
    :param output_dir: str, where to store the pairwise similarities.
    :param prefixes: list of prefixes, without colons, to keep the
    corresponding nodes for
    :return: True if successful
    """
    success = True

    onto_graph_class = import_grape_class(ontology)

    focus_prefixes = [prefix for prefix in prefixes]

    # Some prefixes are helpful for traversing the graph,
    # but don't need to be included in the final simlarities.
    # TODO: only show these if they're present in the graph
    extra_prefixes = ["BFO", "owl", "PATO"]
    traversal_prefixes = [f"{prefix}:" for prefix in prefixes]
    for prefix in extra_prefixes:
        traversal_prefixes.append(f"{prefix}:")

    print(f"Comparing nodes with these prefixes: {' '.join(focus_prefixes)}")
    print(
        "Also traversing nodes with these prefixes: "
        f"{' '.join(extra_prefixes)}"
    )

    onto_graph = (
        onto_graph_class(directed=True)
        .filter_from_names(
            edge_type_names_to_keep=[predicate],
            node_prefixes_to_keep=traversal_prefixes,
        )
        .remove_disconnected_nodes()
        .to_transposed()
    )

    try:
        onto_graph.must_be_connected()
    except ValueError:
        comps = onto_graph.get_number_of_connected_components()
        num_comps = comps[0]
        max_comp = comps[2]
        warnings.warn(
            "Graph is not fully connected. Will ignore"
            " all but the largest component."
            f" {num_comps} components are present."
            f" Largest component has {max_comp} nodes."
        )
        onto_graph = onto_graph.remove_components(top_k_components=1)

    if not onto_graph.is_directed_acyclic():
        warnings.warn("Graph is not directed acyclic.")
        if onto_graph.has_selfloops():
            sys.exit(
                "Self loops are present."
                " Cannot complete similarity measurement."
                " Exiting..."
            )

    if annot_file:
        counts = dict(
            Counter(
                pd.read_csv(
                    annot_file,
                    sep="\t",
                    skiprows=4,
                ).annot_col
            )
        )
    else:

        # TODO: get more specific counts, not all equivalent values

        counts = dict(
            zip(
                onto_graph.get_node_names(),
                [1] * len(onto_graph.get_node_names()),
            )
        )

    compute_pairwise_sims(
        dag=onto_graph,
        counts=counts,
        cutoff=cutoff,
        prefixes=focus_prefixes,
        path=output_dir,
    )

    return success


def import_grape_class(name) -> object:
    """Dynamically import a Grape class based on its reference.

    It's assumed to be part of KG-OBO, but if not, it will
    look in KG-Hub instead.
    :param reference: The reference or path for the class to be imported.
    :return: The imported class
    """
    mod = __import__(GRAPE_DATA_MOD, fromlist=[name])
    try:
        this_class = getattr(mod, name)
    except AttributeError:
        mod = __import__("grape.datasets.kghub", fromlist=[name])
        this_class = getattr(mod, name)
    return this_class
