import streamlit as st
import math
import heapq
import networkx as nx
import matplotlib.pyplot as plt


# Graph, Use Case: Emergency Supply Robot

locations = {
    "Pharmacy": (0, 0),
    "Main_Corridor": (2, 1),
    "Patient_Wing": (1, 4),
    "Nursing_Station": (4, 2),
    "Laboratory": (5, 5),
    "Emergency_Ward": (8, 6)
}

hospital_graph = {
    "Pharmacy": {
        "Main_Corridor": 2.2,
        "Patient_Wing": 4.1
    },

    "Main_Corridor": {
        "Nursing_Station": 2.2
    },

    "Patient_Wing": {
        "Laboratory": 5.0
    },

    "Nursing_Station": {
        "Laboratory": 3.2,
        "Emergency_Ward": 6.0
    },

    "Laboratory": {
        "Emergency_Ward": 3.2
    },

    "Emergency_Ward": {}
}


# Heuristic
def heuristic(current, goal):
    return math.sqrt(
        (locations[current][0] - locations[goal][0]) ** 2 +
        (locations[current][1] - locations[goal][1]) ** 2
    )


# Path reconstruction
def reconstruct_path(came_from, current):
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


# GBFS
def gbfs(start, goal):

    priority_queue = []

    heapq.heappush(
        priority_queue,
        (heuristic(start, goal), start)
    )

    came_from = {}
    visited = set()

    while priority_queue:

        h_value, current = heapq.heappop(priority_queue)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            path = reconstruct_path(came_from, current)

            cost = 0
            for i in range(len(path) - 1):
                cost += hospital_graph[path[i]][path[i + 1]]

            return path, cost

        for neighbor in hospital_graph[current]:

            if neighbor not in visited:

                if neighbor not in came_from:
                    came_from[neighbor] = current

                heapq.heappush(
                    priority_queue,
                    (heuristic(neighbor, goal), neighbor)
                )

    return None, 0


# A*
def a_star(start, goal):

    priority_queue = []

    g_cost = {start: 0}
    came_from = {}

    heapq.heappush(
        priority_queue,
        (heuristic(start, goal), start)
    )

    visited = set()

    while priority_queue:

        f_value, current = heapq.heappop(priority_queue)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:

            path = reconstruct_path(came_from, current)

            return path, g_cost[current]

        for neighbor, cost in hospital_graph[current].items():

            new_g_cost = g_cost[current] + cost

            if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:

                g_cost[neighbor] = new_g_cost
                came_from[neighbor] = current

                f_cost = (
                    new_g_cost +
                    heuristic(neighbor, goal)
                )

                heapq.heappush(
                    priority_queue,
                    (f_cost, neighbor)
                )

    return None, 0


##########################################
# Streamlit GUI Code

# Set Page Config
st.set_page_config(
    page_title="Emergency Supply Robot",
    page_icon="🏥",
    layout="wide"
)


# Title and description
st.title("🏥 Emergency Supply Robot")
st.write(
    "Use GBFS or A* to find a path between two locations in the hospital."
)


# Define the nodes
nodes = list(hospital_graph.keys())


# Create selectbox for initial node
start = st.selectbox(
    "Select Initial Node",
    nodes,
    index=nodes.index("Pharmacy")
)


# Create selectbox for goal node
goal = st.selectbox(
    "Select Goal Node",
    nodes,
    index=nodes.index("Emergency_Ward")
)


# Create selectbox for algorithm
algorithm = st.selectbox(
    "Select Search Algorithm",
    ["GBFS", "A*"]
)


# Run Search button
if st.button("Run Search"):

    if algorithm == "GBFS":

        path, cost = gbfs(start, goal)

    else:

        path, cost = a_star(start, goal)


    if path is None:

        st.error("No path was found.")

    else:

        # Display result
        st.subheader("Search Result")

        st.write(
            f"Algorithm: {algorithm}"
        )

        st.write(
            f"Solution Path: {' → '.join(path)}"
        )

        st.write(
            f"Total Path Cost: {cost:.2f}"
        )


        # Visualize NetworkX graph

        G = nx.DiGraph()

        for node, neighbors in hospital_graph.items():

            for neighbor, weight in neighbors.items():

                G.add_edge(
                    node,
                    neighbor,
                    weight=weight
                )


        pos = locations


        fig, ax = plt.subplots(
            figsize=(10, 6)
        )


        # Draw all nodes
        nx.draw_networkx_nodes(
            G,
            pos,
            node_size=1800,
            ax=ax
        )


        # Draw all edges
        nx.draw_networkx_edges(
            G,
            pos,
            arrows=True,
            arrowsize=20,
            edge_color="gray",
            ax=ax
        )


        # Draw node labels
        nx.draw_networkx_labels(
            G,
            pos,
            font_size=9,
            font_weight="bold",
            ax=ax
        )


        # Draw edge weights
        edge_labels = nx.get_edge_attributes(
            G,
            "weight"
        )

        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=9,
            ax=ax
        )


        # Highlight solution path
        solution_edges = list(
            zip(path, path[1:])
        )


        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=solution_edges,
            edge_color="red",
            width=3,
            arrows=True,
            arrowsize=20,
            ax=ax
        )


        ax.set_title(
            f"{algorithm} Solution Path"
        )

        ax.axis("off")

        st.pyplot(fig)