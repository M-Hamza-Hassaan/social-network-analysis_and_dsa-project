import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain
import matplotlib.cm as cm
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Enhanced Social Network Analyzer", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f8f9fa;
    border-left: 4px solid #1f77b4;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 5px;
}
.quiz-container {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
.code-snippet {
    background-color: #f1f3f4;
    padding: 1rem;
    border-radius: 5px;
    font-family: 'Courier New', monospace;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_data" not in st.session_state:
    st.session_state.user_data = []
if "user_count" not in st.session_state:
    st.session_state.user_count = 1
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}

# Helper functions
def create_graph():
    """Create NetworkX graph from user data"""
    G = nx.Graph()
    for user, friends in st.session_state.user_data:
        if user and friends:  # Validation
            for friend in friends:
                if friend:  # Additional validation
                    G.add_edge(user, friend)
    return G

def calculate_all_centralities(G):
    """Calculate all centrality measures"""
    try:
        centralities = {}
        centralities['degree'] = nx.degree_centrality(G)
        centralities['closeness'] = nx.closeness_centrality(G)
        centralities['betweenness'] = nx.betweenness_centrality(G)
        
        # PageRank (more robust than eigenvector)
        centralities['pagerank'] = nx.pagerank(G)
        
        # Try eigenvector, fallback to PageRank if fails
        try:
            centralities['eigenvector'] = nx.eigenvector_centrality(G, max_iter=1000)
        except:
            centralities['eigenvector'] = centralities['pagerank']
            
        return centralities
    except Exception as e:
        st.error(f"Error calculating centralities: {e}")
        return None

def get_network_stats(G):
    """Calculate comprehensive network statistics"""
    if G.number_of_nodes() == 0:
        return {}
    
    stats = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
        'components': nx.number_connected_components(G),
        'clustering': nx.average_clustering(G),
    }
    
    # Diameter (only for connected graphs)
    if nx.is_connected(G):
        stats['diameter'] = nx.diameter(G)
        stats['avg_path_length'] = nx.average_shortest_path_length(G)
    else:
        stats['diameter'] = "N/A (disconnected)"
        stats['avg_path_length'] = "N/A (disconnected)"
    
    return stats

def create_interactive_network(G, centralities=None, highlight_node=None):
    """Create interactive Plotly network visualization"""
    if G.number_of_nodes() == 0:
        return None
    
    # Get layout
    pos = nx.spring_layout(G, seed=42, k=3, iterations=50)
    
    # Community detection
    partition = community_louvain.best_partition(G)
    
    # Prepare node data
    node_trace = go.Scatter(
        x=[], y=[], mode='markers+text',
        hovertemplate='<b>%{text}</b><br>' +
                     'Degree: %{customdata[0]:.3f}<br>' +
                     'Betweenness: %{customdata[1]:.3f}<br>' +
                     'Closeness: %{customdata[2]:.3f}<br>' +
                     'PageRank: %{customdata[3]:.3f}<br>' +
                     'Community: %{customdata[4]}<extra></extra>',
        text=[], textposition="middle center",
        customdata=[], marker=dict(size=[], color=[], colorscale='Viridis')
    )
    
    # Prepare edge data
    edge_trace = go.Scatter(x=[], y=[], mode='lines',
                           line=dict(width=2, color='lightgray'),
                           hoverinfo='none')
    
    # Add edges
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)
    
    # Add nodes
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (str(node),)
        
        # Node size based on degree centrality
        if centralities:
            degree_cent = centralities['degree'].get(node, 0)
            betweenness_cent = centralities['betweenness'].get(node, 0)
            closeness_cent = centralities['closeness'].get(node, 0)
            pagerank_cent = centralities['pagerank'].get(node, 0)
            
            node_size = 20 + degree_cent * 30
            node_color = betweenness_cent
        else:
            degree_cent = betweenness_cent = closeness_cent = pagerank_cent = 0
            node_size = 25
            node_color = 0.5
        
        community_id = partition.get(node, 0)
        
        # Highlight selected node
        if highlight_node and node == highlight_node:
            node_size *= 1.5
            node_color = 1.0
        
        node_trace['marker']['size'] += (node_size,)
        node_trace['marker']['color'] += (node_color,)
        node_trace['customdata'] += ([degree_cent, betweenness_cent, 
                                    closeness_cent, pagerank_cent, community_id],)
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=dict(text="Interactive Social Network", font=dict(size=16)),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="Node size = Degree Centrality, Color = Betweenness Centrality",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor='left', yanchor='bottom',
                           font=dict(size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=500
                   ))
    
    return fig

def flashcard(title, meaning, use_case, example=None, math_formula=None):
    """Create educational flashcards"""
    with st.container():
        with st.expander(title, expanded=False):
            st.markdown(f"**📖 Definition:** {meaning}")
            st.markdown(f"**🎯 Use Case:** {use_case}")
            if example:
                st.markdown(f"**💡 Example:** {example}")
            if math_formula:
                st.markdown(f"**🔢 Formula:** {math_formula}")

def show_code_snippet(centrality_type):
    """Show code snippets for different centrality calculations"""
    code_snippets = {
        "degree": """
import networkx as nx

# Calculate degree centrality
degree_centrality = nx.degree_centrality(G)
print(f"Degree centrality: {degree_centrality}")
        """,
        "closeness": """
import networkx as nx

# Calculate closeness centrality
closeness_centrality = nx.closeness_centrality(G)
print(f"Closeness centrality: {closeness_centrality}")
        """,
        "betweenness": """
import networkx as nx

# Calculate betweenness centrality
betweenness_centrality = nx.betweenness_centrality(G)
print(f"Betweenness centrality: {betweenness_centrality}")
        """,
        "pagerank": """
import networkx as nx

# Calculate PageRank
pagerank = nx.pagerank(G)
print(f"PageRank: {pagerank}")
        """
    }
    
    st.code(code_snippets.get(centrality_type, "# Code snippet not available"), language='python')

# Main application
st.markdown('<h1 class="main-header">🌐 Enhanced Social Network Analyzer</h1>', unsafe_allow_html=True)

# Sidebar for quick stats
with st.sidebar:
    st.header("📊 Network Overview")
    
    # Create graph for sidebar stats
    G = create_graph()
    if G.number_of_nodes() > 0:
        stats = get_network_stats(G)
        
        st.metric("Nodes", stats['nodes'])
        st.metric("Edges", stats['edges'])
        st.metric("Density", f"{stats['density']:.3f}")
        st.metric("Avg Degree", f"{stats['avg_degree']:.2f}")
        st.metric("Components", stats['components'])
        st.metric("Clustering", f"{stats['clustering']:.3f}")
        
        if isinstance(stats['diameter'], int):
            st.metric("Diameter", stats['diameter'])
            st.metric("Avg Path Length", f"{stats['avg_path_length']:.2f}")
    else:
        st.info("Add network data to see statistics")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🏗️ Build Network", "📈 Analysis & Visualization", "📚 Learning Hub"])

with tab1:
    st.header("👥 Social Network Builder")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Add Users and Connections")
        
        # Input validation improvements
        with st.form("user_form"):
            name = st.text_input("Your Name", placeholder="Enter your name here...")
            friends_input = st.text_input("Connections (comma separated)", 
                                        placeholder="e.g., Alice, Bob, Charlie")
            
            submitted = st.form_submit_button("➕ Add User")
            
            if submitted:
                if not name.strip():
                    st.error("⚠️ Name cannot be empty!")
                elif not friends_input.strip():
                    st.error("⚠️ Please add at least one connection!")
                else:
                    connections = [f.strip() for f in friends_input.split(",") if f.strip()]
                    if not connections:
                        st.error("⚠️ No valid connections found!")
                    else:
                        st.session_state.user_data.append((name.strip(), connections))
                        st.success(f"✅ Added {name} with {len(connections)} connections!")
                        st.rerun()
    
    with col2:
        st.subheader("Current Network Data")
        if st.session_state.user_data:
            for i, (user, friends) in enumerate(st.session_state.user_data):
                with st.expander(f"👤 {user}", expanded=False):
                    st.write(f"**Connections:** {', '.join(friends)}")
                    if st.button(f"🗑️ Remove {user}", key=f"remove_{i}"):
                        st.session_state.user_data.pop(i)
                        st.rerun()
        else:
            st.info("No users added yet")
        
        if st.button("🔄 Clear All Data"):
            st.session_state.user_data = []
            st.rerun()

with tab2:
    st.header("📊 Network Analysis & Interactive Visualization")
    
    G = create_graph()
    
    if G.number_of_nodes() == 0:
        st.warning("🔍 Please add some network data in the 'Build Network' tab first!")
    else:
        # Calculate centralities
        centralities = calculate_all_centralities(G)
        
        if centralities:
            # Interactive visualization
            st.subheader("🎮 Interactive Network Visualization")
            
            # Node selection for highlighting
            col1, col2 = st.columns([1, 1])
            with col1:
                selected_node = st.selectbox("🎯 Highlight Node:", 
                                           options=["None"] + list(G.nodes()))
                highlight = None if selected_node == "None" else selected_node
            
            with col2:
                centrality_viz = st.selectbox("🎨 Color nodes by:", 
                                            ["Betweenness", "Degree", "Closeness", "PageRank"])
            
            # Create and display interactive graph
            fig = create_interactive_network(G, centralities, highlight)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Node details panel
            if highlight:
                st.subheader(f"🔍 Node Details: {highlight}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Degree Centrality", f"{centralities['degree'][highlight]:.3f}")
                with col2:
                    st.metric("Closeness Centrality", f"{centralities['closeness'][highlight]:.3f}")
                with col3:
                    st.metric("Betweenness Centrality", f"{centralities['betweenness'][highlight]:.3f}")
                with col4:
                    st.metric("PageRank", f"{centralities['pagerank'][highlight]:.3f}")
                
                # Show neighbors
                neighbors = list(G.neighbors(highlight))
                st.write(f"**🔗 Direct Connections ({len(neighbors)}):** {', '.join(neighbors) if neighbors else 'None'}")
            
            st.divider()
            
            # Shortest path analysis
            st.subheader("🛣️ Shortest Path Analysis")
            
            nodes_list = list(G.nodes())
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                start_node = st.selectbox("Start Node:", nodes_list, key="start")
            with col2:
                end_node = st.selectbox("End Node:", nodes_list, key="end")
            with col3:
                if st.button("🔍 Find Path"):
                    if start_node != end_node:
                        try:
                            if nx.has_path(G, start_node, end_node):
                                path = nx.shortest_path(G, start_node, end_node)
                                path_length = len(path) - 1
                                st.success(f"**Path found!** Length: {path_length}")
                                st.write(f"**Route:** {' → '.join(path)}")
                            else:
                                st.error("No path exists between these nodes!")
                        except Exception as e:
                            st.error(f"Error finding path: {e}")
                    else:
                        st.warning("Please select different start and end nodes!")
            
            st.divider()
            
            # Community detection
            st.subheader("🏘️ Community Detection")
            
            partition = community_louvain.best_partition(G)
            num_communities = max(partition.values()) + 1
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write(f"**Communities Detected:** {num_communities}")
                for cid in range(num_communities):
                    members = [node for node, comm in partition.items() if comm == cid]
                    st.write(f"🔸 **Community {cid + 1}:** {', '.join(map(str, members))}")
            
            with col2:
                # Community size distribution
                community_sizes = []
                for cid in range(num_communities):
                    size = len([node for node, comm in partition.items() if comm == cid])
                    community_sizes.append(size)
                
                fig_community = px.bar(
                    x=[f"Community {i+1}" for i in range(num_communities)],
                    y=community_sizes,
                    title="Community Size Distribution",
                    labels={'x': 'Community', 'y': 'Number of Members'}
                )
                st.plotly_chart(fig_community, use_container_width=True)
            
            st.divider()
            
            # Centrality comparison
            st.subheader("📊 Centrality Measures Comparison")
            
            # Create DataFrame for better display
            centrality_df = pd.DataFrame({
                'Node': list(G.nodes()),
                'Degree': [centralities['degree'][node] for node in G.nodes()],
                'Closeness': [centralities['closeness'][node] for node in G.nodes()],
                'Betweenness': [centralities['betweenness'][node] for node in G.nodes()],
                'PageRank': [centralities['pagerank'][node] for node in G.nodes()]
            })
            
            # Sort by selected centrality
            sort_by = st.selectbox("Sort by:", ["Degree", "Closeness", "Betweenness", "PageRank"])
            centrality_df_sorted = centrality_df.sort_values(by=sort_by, ascending=False)
            
            st.dataframe(centrality_df_sorted, use_container_width=True)
            
            # Centrality correlation heatmap
            corr_matrix = centrality_df[['Degree', 'Closeness', 'Betweenness', 'PageRank']].corr()
            
            fig_heatmap = px.imshow(
                corr_matrix,
                title="Centrality Measures Correlation",
                color_continuous_scale="RdBu",
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.header("📚 Learning Hub: Understanding Network Analysis")
    
    # Educational content with improved flashcards
    st.subheader("🎯 Centrality Measures Explained")
    
    flashcard(
        "1. 🔵 Degree Centrality",
        "Measures the number of direct connections a node has, normalized by the maximum possible connections.",
        "Identifies the most popular or well-connected individuals in a network.",
        "In a friendship network, the person with the most friends has the highest degree centrality.",
        "Degree Centrality = degree(v) / (n - 1), where n is the total number of nodes"
    )
    
    flashcard(
        "2. 🟡 Closeness Centrality", 
        "Measures how close a node is to all other nodes in the network based on shortest path distances.",
        "Identifies nodes that can most efficiently spread information to the entire network.",
        "A person who can reach everyone in the network through the shortest chains of relationships.",
        "Closeness Centrality = (n - 1) / Σ d(v, u), where d(v,u) is the shortest path distance"
    )
    
    flashcard(
        "3. 🟠 Betweenness Centrality",
        "Measures how often a node lies on the shortest paths between other pairs of nodes.",
        "Identifies nodes that act as bridges or gatekeepers controlling information flow.",
        "A person who connects different groups and controls communication between them.",
        "Betweenness Centrality = Σ σ(s,t|v) / σ(s,t), where σ(s,t) is the number of shortest paths"
    )
    
    flashcard(
        "4. 🔴 PageRank",
        "Originally developed by Google, it measures the importance of a node based on both the number and quality of connections.",
        "Ranks nodes by considering not just quantity but the importance of their connections.",
        "A researcher cited by other highly-cited researchers has higher PageRank than one cited by less influential researchers.",
        "PR(A) = (1-d)/N + d * Σ PR(T)/C(T), where d is damping factor"
    )
    
    st.divider()
    
    # Code snippets section
    st.subheader("💻 Code Examples")
    
    snippet_type = st.selectbox("Choose centrality measure:", 
                               ["degree", "closeness", "betweenness", "pagerank"])
    
    show_code_snippet(snippet_type)
    
    # Download button for complete code
    complete_code = """
import networkx as nx
import matplotlib.pyplot as plt

# Create a sample graph
G = nx.Graph()
G.add_edges_from([('Alice', 'Bob'), ('Bob', 'Charlie'), ('Charlie', 'David')])

# Calculate all centralities
degree_cent = nx.degree_centrality(G)
closeness_cent = nx.closeness_centrality(G)
betweenness_cent = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

# Print results
print("Degree Centrality:", degree_cent)
print("Closeness Centrality:", closeness_cent)
print("Betweenness Centrality:", betweenness_cent)
print("PageRank:", pagerank)

# Visualize
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=1000, font_size=10, font_weight='bold')
plt.show()
    """
    
    st.download_button(
        label="📥 Download Complete NetworkX Code",
        data=complete_code,
        file_name="networkx_centrality_analysis.py",
        mime="text/plain"
    )
    
    st.divider()
    
    # Additional concepts
    st.subheader("🔬 Advanced Network Concepts")
    
    with st.expander("🌐 Network Density", expanded=False):
        st.write("""
        **Definition:** The ratio of existing edges to all possible edges in a network.
        
        **Formula:** Density = 2m / (n(n-1)) for undirected graphs
        
        **Interpretation:** 
        - 0 = No connections
        - 1 = Fully connected (everyone knows everyone)
        - Higher density = More interconnected network
        """)
    
    with st.expander("🔗 Clustering Coefficient", expanded=False):
        st.write("""
        **Definition:** Measures how much nodes tend to cluster together.
        
        **Interpretation:**
        - Measures the probability that two neighbors of a node are also neighbors of each other
        - High clustering = Groups of tightly connected friends
        - Common in social networks (friends of friends are often friends)
        """)
    
    with st.expander("🌉 Connected Components", expanded=False):
        st.write("""
        **Definition:** Subgroups within a network where every node can reach every other node.
        
        **Use Cases:**
        - Identify isolated groups
        - Find disconnected communities
        - Analyze network fragmentation
        """)

# Footer
st.divider()
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌐 <strong>Enhanced Social Network Analyzer</strong></p>
    <p>Built with Streamlit, NetworkX, and Plotly | Learn • Analyze • Visualize</p>
    <p>Built by Muhammad Hamza Hassaan</p>
</div>
""", unsafe_allow_html=True)