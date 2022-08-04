"""Process ontology and retrieve pairwise similarities."""
from collections import Counter

import pandas as pd

from .compute_pairwise_similarities import (
    compute_pairwise_ancestors_jaccard,
    compute_pairwise_resnik,
)


def get_similarities(
    ontology: str, resnik_path: str, ancestors_jaccard_path: str
):
    """Compute and store similarities to the provided paths.

    Parameters
    -----------------------
    ontology: str
        Name of ontology to retrieve and process.
    resnik_path: str
        Where to store the resnik pairwise similarities.
    ancestors_jaccard_path: str
        Where to store the Ancestors Jaccard pairwise similarities.
    """

    ontology = ontology.upper()
    onto_graph_class_name = f"grape.datasets.kgobo.{ontology}"
    onto_graph_class = dynamically_import_class(onto_graph_class_name)

    onto_graph = (
        onto_graph_class(directed=True)
        .filter_from_names(
            edge_type_names_to_keep=["biolink:subclass_of"],
            node_prefixes_to_keep=[f"{ontology}:"],
        )
        .to_transposed()
        .remove_disconnected_nodes()
    )

    counts = dict(
        Counter(
            pd.read_csv(
                "http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa",
                sep="\t",
                skiprows=4,
            ).HPO_ID
        )
    )

    compute_pairwise_ancestors_jaccard(dag=onto_graph, path=ancestors_jaccard_path)

    compute_pairwise_resnik(
        dag=onto_graph, counts=counts, path=ancestors_jaccard_path
    )

def dynamically_import_class(name) -> object:
    """Dynamically import a class based on its reference.
    :param reference: The reference or path for the class to be imported.
    :return: The imported class
    """

    components = name.split(".")
    mod = __import__(components[0])
    for comp in components[1:]:
        this_class = getattr(mod, comp)
    return this_class

