"""Run the semantic similarity pipeline."""
import os

import click

from semsim.process_ontology import get_similarities


@click.group()
def main():
    """CLI for semsim."""
    pass


@main.command()
@click.option("--output", "-o", required=False, default="data")
@click.option("--annot_col", "-c", required=False, default="HPO_ID")
@click.argument("ontology", default="HP")
def run(ontology: str, annot_col: str, output_dir: str) -> None:
    """Generate a file containing the semantic similarity.

    (Resnik and Jaccard) for each pair of terms in an ontology
    (by default, ontology is HP).

    :param ontology: An OBO Foundry ontology on which to compute sem sim [HP]
    :param output_dir: Path to write file of all by all sem sim measurements
    :param annot_col: name of column in annotation file containing onto IDs
    :return: None
    """
    print(f"ontology is {ontology}")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # get ontology, make into DAG
    # make counts (Dict[curie, count])
    # call compute pairwise similarity
    # write out
    outpaths = get_similarities(
        ontology=ontology,
        annot_col=annot_col,
        resnik_path=os.path.join(output_dir, f"{ontology}_resnik"),
        ancestors_jaccard_path=os.path.join(output_dir, f"{ontology}_jaccard"),
    )

    print(outpaths)

    return None


@main.command()
@click.option("--output", "-o", required=False, default="data")
@click.option("--mp_hp_mapping_file", "-m", required=True)
@click.option("--hp_hp_resnik_sim_file", "-h", required=True)
@click.option("--hp_hp_jaccard_sim_file", "-h", required=True)
@click.option("--cutoff", "-c", required=True, default=2.5)
def mp_hp(
    cutoff: str,
    hp_hp_jaccard_sim_file: str,
    hp_hp_resnik_sim_file: str,
    mp_hp_mapping_file: str,
    output_dir: str,
) -> None:
    """Produce an MP-HP phenodigm file.
    That is, a file containing the Resnik and Jaccard similarity
    for pairs of MP-HP phenotypes that meet some minimal level of
    Resnik similarity (default: 2.5).

    :param cutoff: cutoff HP-HP resnik similarity in order to keep a row
    :param hp_hp_jaccard_sim_file: all pairwse HP-HP Jaccard scores
        (produced from run command)
    :param hp_hp_resnik_sim_file: all pairwise HP-HP Resnik scores
        (produced from run commnad)
    :param mp_hp_mapping_file: file containing all equivalent MP-HP phenotypes
    :param output_dir: where to write out file
    :return: None
    """

    # read HP-HP Jaccard sim data into pd dataframe
    # read HP-HP Resnik sim data into pd dataframe
    # read in mp_hp_mapping_file mapping file
    # foreach pair P of equivalent MP-HP terms
    #    select row R for HP term in Resnik
    #    select HP column names HPC in row R for cols in which value > cutoff
    #    for each HPC:
    #        write 1 row in output file for HP term, MP term, Resnik, Jaccard, subsuming HP term

    # We should recreate this phenodigm file format:
    # HP_3000028      MP_0006153      0.2647058823529412      2.5123772659440853      HP_0000271;
    # HP_3000028      MP_0006152      0.25    2.5123772659440853      HP_0000271;

    return None


if __name__ == "__main__":
    main()
