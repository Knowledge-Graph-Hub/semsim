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
    # and load them if they're present
    for filepath in [
        same_jaccard_sim_file,
        same_resnik_sim_file,
        mapping_file,
    ]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Cannot find {filepath}!")
        else:
            print(f"Loading {filepath}...")
        if filepath.endswith("jaccard"):
            jaccard_df = pd.read_csv(filepath, sep="\t", engine="c")
        if filepath.endswith("resnik"):
            resnik_df = pd.read_csv(filepath, sep="\t", engine="c")
        if filepath.endswith("upheno_mapping_all.csv"):
            map_df = pd.read_csv(
                filepath, sep=",", engine="c", usecols=["p1", "p2"]
            )
            filtermap_df = make_hp_mp_map(map_df)

    #   with open(outpath,'w') as outfile:

    return outpath


def make_hp_mp_map(all_map: pd.DataFrame) -> pd.DataFrame:
    """Produce a map specific to HP vs. MP terms.

    :param all_map: pandas df of two columns,
        with one term in col 1 and the equivalent
        term in col 2.
    :return: pandas df with all HP terms (and only these)
        in col 1 and equivalent MP terms (and only these)
        in col 2.
    """
    for col in ["p1", "p2"]:
        all_map[col] = all_map[col].map(
            lambda x: ((x.split("/"))[-1]).replace("_", ":")
        )
        all_map = all_map[all_map[col].str.contains("HP|MP")]

    for newcol in ["HP_term", "MP_term"]:
        all_map[newcol] = ""
        prefix = (newcol.split("_"))[0]
        for col in ["p1", "p2"]:
            all_map.loc[all_map[col].str.startswith(prefix), newcol] = all_map[
                col
            ]

    return all_map
