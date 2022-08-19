"""Process ontology and retrieve pairwise similarities."""
import warnings
from collections import Counter

import pandas as pd

from .compute_pairwise_similarities import (  # noqa
    compute_pairwise_ancestors_jaccard, compute_pairwise_resnik,)

GRAPE_DATA_MOD = "grape.datasets.kgobo"


def get_similarities(
    ontology: str,
    annot_file: str,
    annot_col: str,
    resnik_path: str,
    ancestors_jaccard_path: str,
    prefixes: list,
):
    """Compute and store similarities to the provided paths.

    :param ontology: str, name of ontology to retrieve and process.
    :param resnik_path: str, where to store the resnik pairwise similarities.
    :param ancestors_jaccard_path: str, where to store the Ancestors Jaccard
    pairwise similarities.
    :param prefixes: list of prefixes, without colons, to keep the
    corresponding nodes for
    """
    onto_graph_class = import_grape_class(ontology)

    keep_prefixes = [f"{prefix}:" for prefix in prefixes]

    onto_graph = (
        onto_graph_class(directed=True)
        .filter_from_names(
            edge_type_names_to_keep=["biolink:subclass_of"],
            node_prefixes_to_keep=keep_prefixes,
        )
        .to_transposed()
        .remove_disconnected_nodes()
    )

    if not onto_graph.is_directed_acyclic():
        raise ValueError("Input graph does not appear to be a DAG.")

    try:
        onto_graph.must_be_connected()
    except ValueError:
        comps = onto_graph.get_number_of_connected_components()
        num_comps = comps[0]
        max_comp = comps[2]
        warnings.warn("Graph is not fully connected. Will ignore"
                      " all but the largest component."
                      f" {num_comps} components are present."
                      f" Largest component has {max_comp} nodes.")

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

        # TODO: get actual counts, not all equivalent values

        counts = dict(zip(onto_graph.get_node_names(),
                          [1] * len(onto_graph.get_node_names())))

    compute_pairwise_ancestors_jaccard(
        dag=onto_graph, path=ancestors_jaccard_path
    )

    compute_pairwise_resnik(dag=onto_graph, counts=counts, path=resnik_path)


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
