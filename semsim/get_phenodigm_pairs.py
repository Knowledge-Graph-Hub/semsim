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

    prefixa = "HP"
    prefixb = "MP"

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
            jaccard_df = pd.read_csv(filepath, sep=",", engine="c")
            jaccard_df.rename({'Unnamed: 0': prefixa}, axis=1, inplace=True)
        if filepath.endswith("resnik"):
            resnik_df = pd.read_csv(filepath, sep=",", engine="c")
            resnik_df.rename({'Unnamed: 0': prefixa}, axis=1, inplace=True)
        if filepath == mapping_file:
            map_df = pd.read_csv(
                filepath, sep=",", engine="c", usecols=["p1", "p2"]
            )
            filtermap_df = make_filtered_map(map_df, prefixa, prefixb)

    # For each A term in the filtered map, get Resnik score above cutoff.
    # specifically, get a list of matching rows and then make a df out
    # of them
    match_data = []
    for term in filtermap_df[prefixa]:
        print(term)
        # matches = resnik_df.iloc[
        #     (resnik_df[0] == term) & (resnik_df[1:] > cutoff)
        # ]
        # for match in matches:
        #     match_data.append(term)

    return outpath


def make_filtered_map(
    all_map: pd.DataFrame, prefixa: str, prefixb: str
) -> pd.DataFrame:
    """Produce a map specific to two specific prefixed terms.

    This makes some assumptions about the input file,
    namely that the terms will be in columns with
    the headers "p1" and "p2", and that
    :param all_map: pandas df of two columns,
        with one term in col 1 and the equivalent
        term in col 2.
    :param prefixA: str, first prefix to filter by
    :param prefixB: str, second prefix to filter by
    :return: pandas df with all prefixa terms (and only these)
        in col 1 and equivalent prefixb terms (and only these)
        in col 2.
    """
    for col in ["p1", "p2"]:
        all_map[col] = all_map[col].map(
            lambda x: ((x.split("/"))[-1]).replace("_", ":")
        )
        all_map = all_map[all_map[col].str.contains(f"{prefixa}|{prefixb}")]

    for newcol in [prefixa, prefixb]:
        all_map[newcol] = ""
        prefix = (newcol.split("_"))[0]
        for col in ["p1", "p2"]:
            all_map.loc[all_map[col].str.startswith(prefix), newcol] = all_map[
                col
            ]

    return all_map
