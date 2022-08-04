"""Run the semantic similarity pipeline."""
import click


@click.group()
def cli():
    """CLI."""
    pass


@cli.command()
@click.option("output_dir", "-o", required=True, default="data/raw")
@click.option(
    "--input",
    "-i",
    callback=lambda _, __, x: x.split(",") if x else [],
    default=["HP"],
    help="""One or more OBO Foundry ontologies to run over,
                     comma-delimited, e.g., HP,GO,ZFA.""",
)
def run(*args, **kwargs) -> None:
    """Run code to produce all by all semantic similarity for a ontology [HPO].

    :return: None
    """
    pass
    return None


if __name__ == "__main__":
    cli()
