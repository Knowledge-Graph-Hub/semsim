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
@click.option("--output_dir", "-o", required=False, default="data")
@click.option("--annot_file", "-a", required=False, default=None)
@click.option("--annot_col", "-c", required=False)
@click.option("--prefixes", "-p",
              callback=lambda _, __, x: x.split(',') if x else [],
              required=True)
@click.argument("ontology", default=None)
def sim(
    ontology: str,
    annot_file: str,
    annot_col: str,
    output_dir: str,
    prefixes: list,
) -> None:
    """Generate a file containing the semantic similarity.

    (Resnik and Jaccard) for each pair of terms in an ontology

    :param ontology: An OBO Foundry ontology on which to compute sem sim
    (e.g., HP)
    :param output_dir: Path to write file of all by all sem sim measurements
    :param annot_file: path to an annotation file, if using specific
    frequencies for Resnik calculation
    :param annot_col: name of column in annotation file containing onto IDs
    :param prefixes: One or more node types to select based on prefix,
    comma-delimited, e.g., HP,MP,UPHENO
    :return: None
    """
    print(f"Input ontology is {ontology}")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if (annot_file and not annot_col) or (annot_col and not annot_file):
        raise ValueError(
            "Need both annot_file and annot_col if using specific freq values."
        )

    # get ontology, make into DAG
    # make counts (Dict[curie, count])
    # call compute pairwise similarity
    # write out
    outpaths = get_similarities(
        ontology=ontology,
        annot_file=annot_file,
        annot_col=annot_col,
        resnik_path=os.path.join(output_dir, f"{ontology}_resnik"),
        ancestors_jaccard_path=os.path.join(output_dir, f"{ontology}_jaccard"),
        prefixes=prefixes,
    )

    print(outpaths)

    return None


@main.command()
@click.option("--output_dir", "-o", required=False, default="data")
@click.option(
    "--mapping",
    "-m",
    required=True,
    default="data/upheno_mapping_all.csv",
)
@click.option(
    "--resnik_sim_file", "-h", required=True, default="data/HP_resnik"
)
@click.option(
    "--jaccard_sim_file", "-h", required=True, default="data/HP_jaccard"
)
@click.option("--cutoff", "-c", required=True, default=2.5)
def phenodigm(
    cutoff: str,
    jaccard_sim_file: str,
    resnik_sim_file: str,
    mapping: str,
    output_dir: str,
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
    outpath = make_phenodigm(
        cutoff=cutoff,
        same_jaccard_sim_file=jaccard_sim_file,
        same_resnik_sim_file=resnik_sim_file,
        mapping_file=mapping,
        outpath=os.path.join(output_dir, "phenodigm_semsim.txt"),
        prefixa="HP",
        prefixb="MP",
    )
    print(f"Wrote to {outpath}.")

    return None


if __name__ == "__main__":
    main()
