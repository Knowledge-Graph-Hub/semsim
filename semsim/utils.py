"""Provide utilities for graph loading."""

import os
import tarfile
from grape import Graph


def load_local_graph(name: str, infile: str) -> Graph:
    """Decompress and load a graph file.

    :name: str, name of graph
    :infile: str, path to tar.gz graph file
    :return: Graph
    """

    # Decompress and look for node/edgelists
    infile_contents = {"Nodes": "", "Edges": ""}
    decomp_infile = tarfile.open(infile)
    outdir = os.path.dirname(infile)
    for filename in decomp_infile.getnames():
        if filename.endswith("_nodes.tsv"):
            infile_contents["Nodes"] = os.path.join(outdir, filename)
            decomp_infile.extract(
                member=filename, path=outdir
            )
        if filename.endswith("_edges.tsv"):
            infile_contents["Edges"] = os.path.join(outdir, filename)
            decomp_infile.extract(
                member=filename, path=outdir
            )

    decomp_infile.close()

    outgraph = Graph.from_csv(
        node_path=infile_contents["Nodes"],
        edge_path=infile_contents["Edges"],
        node_list_separator="\t",
        edge_list_separator="\t",
        node_list_header=True,
        edge_list_header=True,
        nodes_column="id",
        node_list_node_types_column="category",
        edge_list_edge_types_column="predicate",
        sources_column="subject",
        destinations_column="object",
        directed=True,
        name=name,
        verbose=True,
    )

    return outgraph
