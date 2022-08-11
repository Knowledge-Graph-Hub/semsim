"""Test compute_pairwise_similarities."""

import os
from unittest import TestCase

from grape import Graph

from semsim.compute_pairwise_similarities import (
    compute_pairwise_ancestors_jaccard,
    compute_pairwise_resnik
)


class TestComputePairwiseSimilarities(TestCase):
    """Test computation of pairwise similarities."""

    def setUp(self) -> None:
        """Set up."""
        self.test_graph_path_nodes = "tests/resources/test_hpo_nodes.tsv"
        self.test_graph_path_edges = "tests/resources/test_hpo_edges.tsv"
        self.resnik_outpath = "tests/output/resnik_out"
        self.jaccard_outpath = "tests/output/jaccard_out"
        self.test_graph = Graph.from_csv(
            directed=True,
            node_path=self.test_graph_path_nodes,
            edge_path=self.test_graph_path_edges,
            nodes_column="id",
            node_list_node_types_column="category",
            sources_column="subject",
            destinations_column="object",
            edge_list_edge_types_column="predicate",
        ).to_transposed()  # To define root correctly
        self.test_counts = {
            "HP:0000118": 23,
            "HP:0000001": 24,
            "HP:0001507": 1,
            "HP:0001574": 1,
            "HP:0001871": 1,
            "HP:0033127": 1,
            "HP:0025354": 1,
            "HP:0001608": 1,
            "HP:0001197": 1,
            "HP:0000119": 1,
            "HP:0001939": 1,
            "HP:0000707": 1,
            "HP:0025031": 1,
            "HP:0001626": 1,
            "HP:0000818": 1,
            "HP:0025142": 1,
            "HP:0002086": 1,
            "HP:0002715": 1,
            "HP:0000478": 1,
            "HP:0040064": 1,
            "HP:0002664": 1,
            "HP:0000598": 1,
            "HP:0000769": 1,
            "HP:0045027": 1,
            "HP:0000152": 1,
        }

    def test_common_ancestry(self) -> None:
        """Test that two nodes have common ancestor."""
        node1 = "HP:0000152"
        node2 = "HP:0001197"
        rootnode = "HP:0000001"
        path1 = self.test_graph.get_shortest_path_node_names_from_node_names(
            rootnode, node1
        )
        path2 = self.test_graph.get_shortest_path_node_names_from_node_names(
            rootnode, node2
        )
        check = False
        for node in path1:
            if node in path2:
                check = True
                break
        self.assertTrue(check)

    def test_compute_pairwise_resnik(self) -> None:
        """Test pairwise Resnik computation."""
        compute_pairwise_resnik(
            dag=self.test_graph,
            counts=self.test_counts,
            path=self.resnik_outpath,
        )
        self.assertTrue(os.path.exists(self.resnik_outpath))

    def test_compute_pairwise_ancestors_jaccard(self) -> None:
        """Test pairwise Jaccard computation."""
        compute_pairwise_ancestors_jaccard(
            dag=self.test_graph, path=self.jaccard_outpath
        )
        self.assertTrue(os.path.exists(self.jaccard_outpath))
