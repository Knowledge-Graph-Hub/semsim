"""Run the semantic similarity pipeline."""
import os

import click

from semsim.process_ontology import get_similarities


@click.group()
def main():
    """CLI for semsim."""
    pass


@main.command()
@click.option("--output-dir", "-o", required=False, default="data/raw")
@click.argument("ontology", default="HP")
def run(ontology: str, output_dir: str) -> None:
    """Generate a file containing the semantic similarity.

    (Resnik and Jaccard) for each pair of terms in an ontology
    (by default, ontology is HP).

    :param ontology: An OBO Foundry ontology on which to compute sem sim [HP]
    :param output_dir: Path to write file of all by all sem sim measurements
    :return: None
    """
    print(f"ontology is {ontology}")

    # get ontology, make into DAG
    get_similarities(
        ontology=ontology,
        resnik_path=os.path.join(output_dir, f"{ontology}_resnik"),
        ancestors_jaccard_path=os.path.join(output_dir, f"{ontology}_jaccard"),
    )

    # make counts (Dict[curie, count])

    # call compute pairwise similarity

    # merge two results

    # write out
    return None


if __name__ == "__main__":
    main()
