import plotly.graph_objects as go
import networkx as nx
import math
from typing import Dict, Any


def render_plotly_architecture_graph(graph_data: Dict[str, Any], height: int = 650):
    """
    Renders an interactive 2D Directed Graph of AUTOSAR SWCs and Interfaces using Plotly.
    """
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        fig = go.Figure()
        fig.add_annotation(text="No architecture nodes available to visualize.", showarrow=False, font=dict(size=16))
        return fig

    # Create NetworkX graph to compute positions
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n["id"], **n)
    for e in edges:
        G.add_edge(e["source"], e["target"], **e)

    # Compute spring layout
    pos = nx.spring_layout(G, k=1.5, iterations=60, seed=42)

    # Edge traces
    edge_x = []
    edge_y = []
    edge_text = []

    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(f"{edge[0]} ➔ {edge[1]}<br>Interface: {edge[2].get('name', 'N/A')}<br>Type: {edge[2].get('type', 'Sender-Receiver')}")

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color='#94a3b8'),
        hoverinfo='none',
        mode='lines'
    )

    # Node coordinates & colors based on ASIL
    node_x = []
    node_y = []
    node_colors = []
    node_text = []
    node_labels = []

    color_map = {
        "ASIL-D": "#ef4444",  # Red
        "ASIL-C": "#f97316",  # Orange
        "ASIL-B": "#eab308",  # Amber
        "QM": "#3b82f6",      # Blue
        "Inferred SWC": "#8b5cf6"
    }

    for node_id in G.nodes():
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        data = G.nodes[node_id]
        asil = data.get("asil", "ASIL-B")
        comp_type = data.get("type", "Software Component")
        page = data.get("page", 1)

        node_colors.append(color_map.get(asil, "#0284c7"))
        node_labels.append(node_id)
        node_text.append(
            f"<b>{node_id}</b><br>"
            f"Type: {comp_type}<br>"
            f"Safety: <b>{asil}</b><br>"
            f"Defined on Page: {page}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_labels,
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=28,
            line_width=2.5,
            line=dict(color='#ffffff')
        )
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="<b>AUTOSAR Software Component & Interface Topology</b>",
                font=dict(size=16, color="#f8fafc", family="Inter, Segoe UI")
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=height,
            plot_bgcolor='#0b0f19',
            paper_bgcolor='#0b0f19'
        )
    )

    return fig
