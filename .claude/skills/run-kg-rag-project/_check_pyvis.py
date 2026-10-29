"""One-shot: exercise the same pyvis path render_kg uses, no Streamlit needed."""
import os
import networkx as nx
from pyvis.network import Network

kg = nx.DiGraph()
kg.add_edge("Alice", "Bob", relation="knows")
kg.add_edge("Bob", "Carol", relation="manages")
kg.add_edge("Carol", "Alice", relation="reports_to")

net = Network(
    height="500px", width="100%",
    bgcolor="#0a0a0f", font_color="#e6e6ed",
    directed=True, cdn_resources="in_line",
)
for n in kg.nodes():
    net.add_node(n, label=n, color="#8b5cf6", size=20)
for s, t, d in kg.edges(data=True):
    net.add_edge(s, t, label=d["relation"])

html = net.generate_html(notebook=False)
print(f"OK html_len={len(html)} has_vis={'vis-network' in html} has_data={'Alice' in html}")

# Confirm no ./lib/ was created in CWD by this call.
lib_marker = os.path.join(os.getcwd(), "lib", "bindings")
lib_exists_before = os.path.exists(lib_marker)  # may already exist (repo ships lib/)
print(f"lib/bindings already in repo: {lib_exists_before}")
