import os

import click

@click.group()
def cli():
    pass

@cli.command()
@click.option("yaml_file", "-y", required=True, default="download.yaml",
              type=click.Path(exists=True))
@click.option("output_dir", "-o", required=True, default="data/raw")
@click.option("ignore_cache", "-i", is_flag=True, default=False,
              help='ignore cache and download files even if they exist [false]')
def run(*args, **kwargs) -> None:
    """Run code to produce all by all semantic similarity for a given ontology [HPO]

    :return: None
    """
    pass
    return None

if __name__ == "__main__":
    cli()
