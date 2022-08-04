"""Run the semantic similarity pipeline."""
import click


@click.group()
def cli():
    """CLI."""
    pass


@cli.command()
@click.option("--output-dir", "-o", required=False, default="data/raw")
@click.argument(
    "ontology",
    default="HP"
)
def run(ontology: str, output_dir: str) -> None:
    """Generate a file containing the semantic similarity (Resnik and
    Jaccard) for each pair of terms in an ontology (by default, ontology is HP)

    :param ontology: An OBO Foundry ontology on which to compute sem sim [HP]
    :param output_dir: Path to write out file with all by all sem sim measurements
    :return: None
    """
    print(f"ontology is {ontology}")

    # get ontology, make into DAG

    # make counts

    # call compute pairwise similarity

    # merge two results
    return None


if __name__ == "__main__":
    run()


#     """Generate a file containing all by all 
#     semantic similarity for each pair of terms in an ontology
#     (by default, ontology is HP)

#     :param ontology: [An OBO Foundry ontologiy to run over [HP]""",
# ]
#     :type ontology: [type]
#     :param output_dir: [description]
#     :type output_dir: [type]
#     :return: [description]
#     :rtype: [type]
#     """