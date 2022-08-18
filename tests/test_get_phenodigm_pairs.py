"""Test get_phenodigm_pairs."""


import os
from unittest import TestCase

import pandas as pd

from semsim.get_phenodigm_pairs import make_filtered_map, make_phenodigm


class TestGetPhenodigmPairs(TestCase):
    """Test production of Phenodigm-style similarity pairs."""

    def setUp(self) -> None:
        """Set up."""
        self.cutoff = "2"
        self.test_jaccard_sim_file = "tests/resources/test_jaccard"
        self.test_resnik_sim_file = "tests/resources/test_resnik"
        self.mapping_file = "tests/resources/test_mapping.csv"
        self.outpath = "tests/output/phenodigm_out"
        self.prefixa = "HP"
        self.prefixb = "MP"

    def test_make_phenodigm(self) -> None:
        """Test that phenodigm output is as expected."""
        make_phenodigm(
            cutoff=self.cutoff,
            same_jaccard_sim_file=self.test_jaccard_sim_file,
            same_resnik_sim_file=self.test_resnik_sim_file,
            mapping_file=self.mapping_file,
            outpath=self.outpath,
            prefixa=self.prefixa,
            prefixb=self.prefixb,
        )
        self.assertTrue(os.path.exists(self.outpath))

    def test_make_filtered_map(self) -> None:
        """Test that prefix-filtered map is as expected."""
        map_df = pd.read_csv(
            self.mapping_file, sep=",", engine="c", usecols=["p1", "p2"]
        )
        filtermap_df = make_filtered_map(map_df, self.prefixa, self.prefixb)
        col1 = self.prefixa + "_id"
        col2 = self.prefixb + "_id"
        self.assertTrue(filtermap_df[col1].str.startswith(self.prefixa).all())
        self.assertTrue(filtermap_df[col2].str.startswith(self.prefixb).all())
