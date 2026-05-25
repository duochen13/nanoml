"""Parser aggregator that scans code and extracts lineage."""

import os
from pathlib import Path
from typing import List, Dict, Any
from .base import LineageNode, LineageEdge
from .spark import SparkParser
from .mlflow import MLflowParser
from .airflow import AirflowParser


class LineageParserAggregator:
    """Scans project files and extracts lineage relationships."""

    def __init__(self):
        """Initialize parser aggregator."""
        self.parsers = [
            SparkParser(),
            MLflowParser(),
            AirflowParser(),
        ]

    def scan_directory(self, directory: str, extensions: List[str] = [".py"]) -> Dict[str, Any]:
        """Scan a directory for Python files and extract lineage.

        Args:
            directory: Directory to scan
            extensions: File extensions to look for

        Returns:
            Dictionary with nodes and edges representing the lineage graph
        """
        all_nodes = []
        all_edges = []
        parsed_files = []

        # Walk through directory
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)

                    # Try each parser
                    for parser in self.parsers:
                        if parser.can_parse(file_path):
                            try:
                                nodes, edges = parser.parse_file(file_path)
                                all_nodes.extend(nodes)
                                all_edges.extend(edges)
                                parsed_files.append({
                                    "file": file_path,
                                    "parser": parser.__class__.__name__,
                                    "nodes_found": len(nodes),
                                    "edges_found": len(edges)
                                })
                            except Exception as e:
                                print(f"Error parsing {file_path}: {e}")
                            break  # Only use first matching parser

        # Deduplicate nodes by ID
        unique_nodes = {}
        for node in all_nodes:
            if node.id not in unique_nodes:
                unique_nodes[node.id] = node
            else:
                # Merge metadata
                unique_nodes[node.id].metadata.update(node.metadata)

        # Deduplicate edges
        unique_edges = {}
        for edge in all_edges:
            edge_key = f"{edge.source_id}->{edge.target_id}->{edge.relation_type.value}"
            if edge_key not in unique_edges:
                unique_edges[edge_key] = edge

        return {
            "nodes": [node.to_dict() for node in unique_nodes.values()],
            "edges": [edge.to_dict() for edge in unique_edges.values()],
            "stats": {
                "total_nodes": len(unique_nodes),
                "total_edges": len(unique_edges),
                "files_parsed": len(parsed_files),
                "parsed_files": parsed_files
            }
        }

    def build_impact_graph(self, lineage_data: Dict[str, Any], node_id: str) -> Dict[str, Any]:
        """Build impact graph showing what's affected by a node change.

        Args:
            lineage_data: Lineage data from scan_directory
            node_id: ID of the node to analyze

        Returns:
            Dictionary with upstream and downstream nodes
        """
        nodes = {n["id"]: n for n in lineage_data["nodes"]}
        edges = lineage_data["edges"]

        # Find downstream (what this node affects)
        downstream = set()
        self._find_downstream(node_id, edges, downstream)

        # Find upstream (what affects this node)
        upstream = set()
        self._find_upstream(node_id, edges, upstream)

        return {
            "node": nodes.get(node_id),
            "upstream": [nodes[nid] for nid in upstream if nid in nodes],
            "downstream": [nodes[nid] for nid in downstream if nid in nodes],
            "impact_score": len(downstream)  # How many things break if this changes
        }

    def _find_downstream(self, node_id: str, edges: List[Dict], visited: set):
        """Recursively find all downstream nodes."""
        for edge in edges:
            if edge["source"] == node_id and edge["target"] not in visited:
                visited.add(edge["target"])
                self._find_downstream(edge["target"], edges, visited)

    def _find_upstream(self, node_id: str, edges: List[Dict], visited: set):
        """Recursively find all upstream nodes."""
        for edge in edges:
            if edge["target"] == node_id and edge["source"] not in visited:
                visited.add(edge["source"])
                self._find_upstream(edge["source"], edges, visited)
