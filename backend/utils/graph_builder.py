import networkx as nx
from typing import List, Dict, Any
from backend.models.schemas import ComponentBase, InterfaceBase


class ArchitectureGraphBuilder:
    def build_graph(self, components: List[Any], interfaces: List[Any]) -> Dict[str, Any]:
        """
        Build a NetworkX directed graph from components and interfaces.
        Returns node/edge metadata, cycles, orphaned components, and centrality.
        """
        G = nx.DiGraph()

        # Add nodes
        for comp in components:
            name = comp.name if hasattr(comp, 'name') else comp.get('name')
            comp_type = comp.type if hasattr(comp, 'type') else comp.get('type', 'SWC')
            asil = comp.asil_level if hasattr(comp, 'asil_level') else comp.get('asil_level', 'ASIL-B')
            page = comp.page if hasattr(comp, 'page') else comp.get('page', 1)

            G.add_node(name, type=comp_type, asil=asil, page=page)

        # Add edges
        for ifc in interfaces:
            src = ifc.source if hasattr(ifc, 'source') else ifc.get('source')
            tgt = ifc.target if hasattr(ifc, 'target') else ifc.get('target')
            name = ifc.name if hasattr(ifc, 'name') else ifc.get('name')
            iface_type = ifc.interface_type if hasattr(ifc, 'interface_type') else ifc.get('interface_type', 'Sender-Receiver')

            if src and tgt:
                if not G.has_node(src):
                    G.add_node(src, type="Inferred SWC", asil="QM", page=1)
                if not G.has_node(tgt):
                    G.add_node(tgt, type="Inferred SWC", asil="QM", page=1)

                G.add_edge(src, tgt, name=name, type=iface_type)

        # Graph Analytics
        nodes_list = [{"id": n, **G.nodes[n]} for n in G.nodes()]
        edges_list = [{"source": u, "target": v, **G.edges[u, v]} for u, v in G.edges()]

        # Cycles detection
        try:
            cycles = list(nx.simple_cycles(G))
        except Exception:
            cycles = []

        # Orphaned nodes (isolated)
        orphans = [n for n, deg in G.degree() if deg == 0]

        # In-degree / Out-degree
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())

        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "node_count": len(nodes_list),
            "edge_count": len(edges_list),
            "cycles": cycles,
            "orphans": orphans,
            "in_degree": in_degree,
            "out_degree": out_degree
        }


graph_builder = ArchitectureGraphBuilder()
