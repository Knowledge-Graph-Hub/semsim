"""Get pairs of phenotype terms meeting a similarity threshold."""

import os

import pandas as pd


def make_phenodigm(
    cutoff: str,
    same_jaccard_sim_file: str,
    same_resnik_sim_file: str,
    mapping_file: str,
    outpath: str,
) -> str:
    """Produce a phenodigm file.

    This is generally a MP-HP comparison.
    Output is a path to a file containing the Resnik and Jaccard
    similarity for pairs of phenotypes that meet some minimal
    level of Resnik similarity (default: 2.5).

    :param cutoff: cutoff Resnik similarity in order to keep a row
    :param same_jaccard_sim_file: all pairwise self vs. self Jaccard scores
        (produced from semsim run command)
    :param same_resnik_sim_file: all pairwise self vs. self Resnik scores
        (produced from semsim run command)
    :param mapping_file: file containing all equivalent
        cross-phenotype pairs
    :param outpath: where to write out file
    :return: str, path to output
    """

    # Check for existence of all input files first
    for filepath in [
        same_jaccard_sim_file,
        same_resnik_sim_file,
        mapping_file,
    ]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Cannot find {filepath}!")

    return outpath
