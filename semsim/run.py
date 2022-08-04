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
    help="""An OBO Foundry ontologiy to run over [HP]"""
)
def run(ontology, output_dir, **kwargs) -> None:
    """Run code to produce all by all semantic similarity for a ontology [HPO].

    :return: None
    """
    print(f"ontology is {ontology}")
    return None


if __name__ == "__main__":
    cli()
