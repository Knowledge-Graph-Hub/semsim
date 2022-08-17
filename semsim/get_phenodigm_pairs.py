"""Get pairs of phenotype terms meeting a similarity threshold."""

import os

import pandas as pd
from tqdm import tqdm


def make_phenodigm(
    cutoff: str,
    same_jaccard_sim_file: str,
    same_resnik_sim_file: str,
    mapping_file: str,
    outpath: str,
    prefixa: str,
    prefixb: str,
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
    :param prefixa: prefix of first ontology, e.g. 'HP'
    :param prefixb: prefix of second ontology, e.g. 'MP'
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
            jaccard_df = pd.read_csv(filepath, sep=",", engine="c")
            jaccard_df.rename({"Unnamed: 0": prefixa}, axis=1, inplace=True)
        if filepath.endswith("resnik"):
            resnik_df = pd.read_csv(filepath, sep=",", engine="c")
            resnik_df.rename({"Unnamed: 0": prefixa}, axis=1, inplace=True)
        if filepath == mapping_file:
            map_df = pd.read_csv(
                filepath, sep=",", engine="c", usecols=["p1", "p2"]
            )
            filtermap_df = make_filtered_map(map_df, prefixa, prefixb)

    # For each A term in the filtered map, get Resnik score above cutoff.
    # specifically, get a list of matching rows and then make a df out
    # of them
    match_data = []  # List of lists, for efficiency
    error_data = []
    print(
        f"Finding {prefixa} term matches based on Resnik scores, "
        f"cutoff {cutoff}..."
    )

    # TODO: ignore duplicates when appending to match_data

    for term in tqdm(set(filtermap_df[prefixa + "_id"])):
        rmatches = resnik_df.loc[(resnik_df[prefixa] == term)]
        jmatches = jaccard_df.loc[(jaccard_df[prefixa] == term)]
        for match in rmatches.iloc[0:1, 1:]:
            try:
                if float(rmatches[match].values[0]) > float(cutoff):
                    match_data.append(
                        [
                            term,
                            match,
                            jmatches[match].values[0],
                            rmatches[match].values[0],
                        ]
                    )
            except (TypeError, IndexError):
                error_data.append(term)  # Some terms may not have scores

    # Jaccard score and Resnik score
    full_df = pd.DataFrame(
        match_data, columns=[prefixa, prefixb, "jaccard", "resnik"]
    )

    # Include MP term
    full_df = pd.merge(
        left=full_df,
        right=filtermap_df,
        how="inner",
        left_on=prefixb,
        right_on=prefixa + "_id",
    )

    # TODO: Include subsumer term

    # Clean up the df before writing
    # Also do some reformatting to match expected
    full_df.drop(columns=[prefixb, prefixa + "_id"], inplace=True)
    full_df.rename({prefixb + "_id": prefixb}, axis=1, inplace=True)
    full_df.insert(1, prefixb, full_df.pop(prefixb))
    for col in [prefixa, prefixb]:
        full_df[col] = full_df[col].str.replace(':', '_')

    full_df.to_csv(outpath, index=False, header=False, sep='\t')

    if len(error_data) > 0:
        print("The following terms had errors:")
        print("\n".join(list(set(error_data))))

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

    all_map.drop(columns=["p1", "p2"], inplace=True)
    all_map.rename(
        {prefixa: prefixa + "_id", prefixb: prefixb + "_id"},
        axis=1,
        inplace=True,
    )

    return all_map
