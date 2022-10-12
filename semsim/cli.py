"""Run the semantic similarity pipeline."""
import os

import click

from semsim.get_phenodigm_pairs import make_phenodigm
from semsim.process_ontology import get_similarities


@click.group()
def main():
    """CLI for semsim."""
    pass


@main.command()
@click.option("--cutoff", "-c", required=True, default=2.5)
@click.option("--output_dir", "-o", required=False, default="data")
@click.option("--annot_file", "-a", required=False, default=None)
@click.option("--annot_col", "-c", required=False)
@click.option(
    "--prefixes",
    "-p",
    callback=lambda _, __, x: x.split(",") if x else [],
    required=False,
)
@click.option(
    "--predicate", "-r", required=True, default="biolink:subclass_of"
)
@click.option(
    "--root_node", "-n", required=True, default=""
)
@click.argument("ontology", default=None)
def sim(
    ontology: str,
    cutoff: str,
    annot_file: str,
    annot_col: str,
    output_dir: str,
    prefixes: list,
    predicate: str,
    root_node: str,
) -> None:
    """Generate a file containing the semantic similarity.

    (Resnik and Jaccard) for each pair of terms in an ontology

    :param ontology: An OBO Foundry ontology on which to compute sem sim
    (e.g., HP)
    :param cutoff: cutoff Resnik similarity in order to keep a row
    :param output_dir: Path to write file of all by all sem sim measurements
    :param annot_file: path to an annotation file, if using specific
    frequencies for Resnik calculation
    :param annot_col: name of column in annotation file containing onto IDs
    :param prefixes: One or more node types to calculate
    similarity scores for, comma-delimited, e.g., HP,MP
    :param predicate: A predicate type to filter on.
    Defaults to biolink:subclass_of.
    :param root_node: specify the name of a node to use as root,
    specifically for Jaccard calculations.
    :return: None
    """
    print(f"Input graph is {ontology}.")
    print(f"Filtering to {predicate}.")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if (annot_file and not annot_col) or (annot_col and not annot_file):
        raise ValueError(
            "Need both annot_file and annot_col if using specific freq values."
        )

    cutoff = float(cutoff)

    if not prefixes:
        prefixes = [ontology]

    # get ontology, make into DAG
    # make counts (Dict[curie, count])
    # call compute pairwise similarity
    # write out
    if get_similarities(
        ontology=ontology,
        cutoff=cutoff,
        annot_file=annot_file,
        annot_col=annot_col,
        output_dir=output_dir,
        nodes=prefixes,
        predicate=predicate,
        root_node=root_node,
        subset=False,
        root_node=root_node,
    ):
        print(f"Wrote to {output_dir}.")
    else:
        print(f"Semantic similarity calculation failed for {ontology}.")

    return None


@main.command()
@click.option(
    "--participants",
    "-p",
    callback=lambda _, __, x: x.split(",") if x else [],
    required=True,
)
@click.option(
    "--predicate", "-r", required=True, default="biolink:subclass_of"
)
@click.argument("ontology", default=None)
def somesim(
    ontology: str,
    participants: list,
    predicate: str,
) -> dict:
    """Return the semantic similarity for a list of nodes.

    Output will be a dict of tuples, with each pair as a key.

    :param ontology: An OBO Foundry ontology on which to compute sem sim
    (e.g., HP)
    :param participants: No fewer than two classes/nodes to return
    similarity scores for, comma-delimited, e.g., HP:0500167,MP:0004731
    :param predicate: A predicate type to filter on.
    Defaults to biolink:subclass_of.
    :return: dict of tuples, with the IDs of each pair (a tuple) as
    the key and a tuple of (Resnik, Jaccard) as value.
    """
    print(f"Input graph is {ontology}.")
    print(f"Filtering to {predicate}.")

    # get ontology, make into DAG
    # make counts (Dict[curie, count])
    # call compute pairwise similarity
    # write out
    sims = get_similarities(
        ontology=ontology,
        cutoff=0,
        annot_file=None,
        annot_col=None,
        output_dir=None,
        nodes=participants,
        predicate=predicate,
        subset=True,
    )

    print(sims)
    return sims


@main.command()
@click.option("--output_dir", "-o", required=False, default="data")
@click.option(
    "--mapping",
    "-m",
    required=True,
    default="data/upheno_mapping_all.csv",
)
@click.option("--resnik_sim_file", "-r", required=True)
@click.option("--jaccard_sim_file", "-j", required=True)
@click.option("--cutoff", "-c", required=True, default=2.5)
@click.option(
    "--prefixes",
    "-p",
    callback=lambda _, __, x: x.split(",") if x else [],
    required=True,
)
def phenodigm(
    cutoff: str,
    jaccard_sim_file: str,
    resnik_sim_file: str,
    mapping: str,
    output_dir: str,
    prefixes: list,
) -> None:
    """Produce phenodigm-style similarity input file.

    That is, a file containing the Resnik and Jaccard similarity
    for pairs of terms that meet some minimal level of
    Resnik similarity (default: 2.5).

    :param cutoff: cutoff Resnik similarity in order to keep a row
    :param jaccard_sim_file: all pairwise Jaccard scores
        (produced from sim command)
    :param resnik_sim_file: all pairwise Resnik scores
        (produced from sim commnad)
    :param mapping: file containing all equivalent terms
    :param output_dir: where to write out file
    :return: None
    """
    if len(prefixes) > 2 or len(prefixes) < 2:
        raise ValueError("Only pairs of prefixes are supported.")
    else:
        prefixa = prefixes[0]
        prefixb = prefixes[1]

    outpath = make_phenodigm(
        cutoff=cutoff,
        same_jaccard_sim_file=jaccard_sim_file,
        same_resnik_sim_file=resnik_sim_file,
        mapping_file=mapping,
        outpath=os.path.join(output_dir, "phenodigm_semsim.txt"),
        prefixa=prefixa,
        prefixb=prefixb,
    )
    print(f"Wrote to {outpath}.")

    return None


if __name__ == "__main__":
    main()
