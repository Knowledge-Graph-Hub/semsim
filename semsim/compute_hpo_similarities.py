from grape.datasets.kgobo import HP
from  collections import Counter
import pandas as pd
from .compute_pairwise_similarities import compute_pairwise_ancestors_jaccard, compute_pairwise_resnik

def compute_hpo_similarities(
    resnik_path: str,
    ancestors_jaccard_path: str
):
    """Computes and stores similarities to the provided paths.
    
    Parameters
    -----------------------
    resnik_path: str
        Where to store the resnik pairwise similarities.
    ancestors_jaccard_path: str
        Where to store the Ancestors Jaccard pairwise similarities.
    """
    hpo = HP(directed=True)\
        .filter_from_names(
            edge_type_names_to_keep=["biolink:subclass_of"],
            node_prefixes_to_keep=["HP:"]
        )\
        .to_transposed()\
        .remove_disconnected_nodes()
    
    counts = dict(Counter(
        pd.read_csv(
            "http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa",
            sep="\t",
            skiprows=4
        ).HPO_ID
    ))

    compute_pairwise_ancestors_jaccard(
        dag=hpo,
        path=ancestors_jaccard_path
    )

    compute_pairwise_resnik(
        dag=hpo,
        counts=counts,
        path=ancestors_jaccard_path
    )