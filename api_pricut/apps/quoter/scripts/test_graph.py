import networkx as nx
import math


# Function to calculate the angle between two points
def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


# Function to traverse the graph in a clockwise direction
def traverse_clockwise(G, start_node):
    current_node = start_node
    visited_edges = set()
    path = [current_node]

    while True:
        neighbors = list(G.neighbors(current_node))
        if len(neighbors) == 0:
            break

        # Sort neighbors by angle in clockwise direction
        neighbors.sort(
            key=lambda x: calculate_angle(current_node, x), reverse=True
        )
        # Find the next edge that has not been visited
        next_node = None
        for neighbor in neighbors:
            if (current_node, neighbor) not in visited_edges and (
                neighbor,
                current_node,
            ) not in visited_edges:
                next_node = neighbor
                break

        if next_node is None:
            break

        # Mark the edge as visited
        visited_edges.add((current_node, next_node))
        visited_edges.add((next_node, current_node))

        # Move to the next node
        current_node = next_node
        path.append(current_node)

        # If we have returned to the start node, stop
        if current_node == start_node:
            break

    return path


def run():
    """
    FIGURA ORDENADA Y SIGUIENDO EL SENTIDO DE LAS AGUJAS DEL RELOJ
    lines = [
        ((0.0, 0.0), (10.0, 0.0)),
        ((10.0, 0.0), (15.0, 5.0)),
        ((15.0, 5.0), (10.0, 10.0)),
        ((10.0, 10.0), (0.0, 10.0)),
        ((0.0, 10.0), (0.0, 0.0)),
    ]

    FIGURA DESORDENADA Y SIGUIENDO EL SENTIDO DE LAS AGUJAS DEL RELOJ
    lines = [
        ((10.0, 0.0), (15.0, 5.0)),
        ((0.0, 0.0), (10.0, 0.0)),
        ((15.0, 5.0), (10.0, 10.0)),
        ((0.0, 10.0), (0.0, 0.0)),
        ((10.0, 10.0), (0.0, 10.0)),
    ]

    FIGURA DESORDENADA CON LINEAS INVERTIDAS
    lines = [
        ((15.0, 5.0), (10.0, 0.0)), # INVERTIDA
        ((0.0, 0.0), (10.0, 0.0)),
        ((15.0, 5.0), (10.0, 10.0)),
        ((0.0, 0.0), (0.0, 10.0)), # INVERTIDA
        ((10.0, 10.0), (0.0, 10.0)),
    ]

    FIGURA ORDENADA Y SIGUIENDO EL SENTIDO DE LAS AGUJAS DEL RELOJ Y CON LINEAS DUPLICADAS
    lines = [
        ((0.0, 0.0), (10.0, 0.0)),
        ((0.0, 0.0), (10.0, 0.0)),
        ((10.0, 10.0), (0.0, 10.0)),
        ((10.0, 0.0), (15.0, 5.0)),
        ((15.0, 5.0), (10.0, 10.0)),
        ((10.0, 10.0), (0.0, 10.0)),
        ((0.0, 10.0), (0.0, 0.0)),
    ]

    FIGURA ORDENADA Y SIGUIENDO EL SENTIDO DE LAS AGUJAS DEL RELOJ Y CON LINEAS DUPLICADAS E INVERTIDAS
    lines = [
        ((15.0, 5.0), (10.0, 0.0)), # INVERTIDA
        ((0.0, 0.0), (10.0, 0.0)),
        ((15.0, 5.0), (10.0, 0.0)), # INVERTIDA
        ((15.0, 5.0), (10.0, 10.0)),
        ((0.0, 0.0), (0.0, 10.0)), # INVERTIDA
        ((10.0, 10.0), (0.0, 10.0)),
        ((0.0, 0.0), (10.0, 0.0)),
    ]
    """

    graph = nx.Graph()
    # print(type(graph))
    lines = [
        ((15.0, 5.0), (10.0, 0.0)),  # INVERTIDA
        ((0.0, 0.0), (10.0, 0.0)),
        ((15.0, 5.0), (10.0, 0.0)),  # INVERTIDA
        ((15.0, 5.0), (10.0, 10.0)),
        ((0.0, 0.0), (0.0, 10.0)),  # INVERTIDA
        ((10.0, 10.0), (0.0, 10.0)),
        ((0.0, 0.0), (10.0, 0.0)),
    ]
    # Add the lines to the graph
    for line in lines:
        vertex_start, vertex_end = line
        graph.add_edge(vertex_start, vertex_end, line=line)

    # Find the connected components
    components = list(nx.connected_components(G=graph))

    # Extract edges for each connected component
    components_with_edges = []
    for component in components:

        subgraph = graph.subgraph(nodes=component)
        edges = list(subgraph.edges)
        print(edges)
        print(type(edges[0][0][0]))
        components_with_edges.append((subgraph, edges))

    # print(components_with_edges)

    for subgraph, edges in components_with_edges:
        start_node = edges[0][0]
        path = traverse_clockwise(subgraph, start_node)
        print(path)
