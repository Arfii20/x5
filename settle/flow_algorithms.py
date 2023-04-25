import copy

import settle.flow as flow


class PathError(Exception):
    ...


class NoSimplification(Exception):
    ...


class MaxFlow:
    @staticmethod
    def edmunds_karp(graph: flow.FlowGraph, src: flow.Vertex, sink: flow.Vertex) -> int:
        """Returns the max flow between src and sink nodes"""
        max_flow = 0
        while aug_path := MaxFlow.augmenting_path(graph, src, sink):
            bottleneck = MaxFlow.bottleneck(graph, aug_path)
            max_flow += bottleneck
            graph.augment_flow(aug_path, bottleneck)
            # graph.draw(f"intra-settle", subdir='test_settle')

        return max_flow

    @staticmethod
    def augmenting_path(
        graph: flow.FlowGraph, src: flow.Vertex, sink: flow.Vertex
    ) -> list[flow.Vertex]:
        """Returns the shortest path from src -> sink"""
        return MaxFlow._bfs(graph, src=src, sink=sink)

    @staticmethod
    def bottleneck(graph: flow.FlowGraph, path: list[flow.Vertex]) -> int:
        """Returns the bottleneck value from a path specified by a list of vertices"""
        # Create a list of edges for each pair of adjacent nodes in the path. Pull the unused capacity from each edge
        # Select the minimum unused capacity
        return min(
            map(
                lambda u, v: graph.get_edge(u, v, residual=True).unused_capacity,
                path,
                path[1:],
            )
        )

    @staticmethod
    def _bfs(
        graph: flow.FlowGraph, src: flow.Vertex, sink: flow.Vertex
    ) -> list[flow.Vertex]:
        """performs a bfs starting from a src node to a sink node; reconstructs the shortest path
        (in terms of edges traversed) from src to sink and returns it."""

        # store vertices of the graph
        vertices = graph.graph.keys()

        # initialise the visited map with all nodes set to false
        visited: dict[flow.Vertex, bool] = {v: False for v in vertices}

        # initialise the came_from map with all nodes set to None
        came_from: dict[flow.Vertex, flow.Vertex | None] = {v: None for v in vertices}

        # initialise the queue; enqueue src node
        queue: list[flow.Vertex] = [src]

        while queue:
            # dequeue into current; mark current as visited
            current = queue.pop(0)
            visited[current] = True

            # if neighbours haven't been visited, enqueue them and mark them as coming from current
            for neighbour in graph.neighbours(current):
                # move on if we have already visited the neighbour
                if visited[neighbour]:
                    continue

                # otherwise enqueue
                queue.append(neighbour)

                # and mark as coming from current node
                came_from[neighbour] = current

                # can exit early if we have just processed the sink node
                if neighbour == sink:
                    break

        return MaxFlow._path_from_map(came_from, src=src, sink=sink)

    @staticmethod
    def _path_from_map(
        came_from: dict[flow.Vertex, flow.Vertex | None],
        *,
        src: flow.Vertex,
        sink: flow.Vertex,
    ) -> list[flow.Vertex]:
        """Builds a path of vertices from the map generated by the bfs"""

        # if nothing has been changed then return an empty list, as no more paths exist
        if list(came_from.values()).count(None) == len(came_from.values()):
            return []

        # raise an error if we don't have a pointer to sink, as no path was found that leads to the sink
        if came_from[sink] is None:
            return []

        # build path backtracking from sink
        path: list[flow.Vertex] = [sink]

        current: flow.Vertex = sink
        while current := came_from[current]:
            # add vertex to front of path if the map doesn't correspond to None
            path.insert(0, current) if current else 0

        # Throw an error if start isn't source or end isn't sink - means the path is broken
        if path[0] != src or path[-1] != sink:
            raise PathError("Broken path: could not generate a path from src -> sink")

        return path


class Settle:
    @staticmethod
    def simplify_debt(debt_network: flow.FlowGraph) -> flow.FlowGraph:
        """Returns the debt network, simplified, in graph form

        in pseudocode

        for edge(u, v) in graph:
            if new := maxflow(u, v):
                clean.add_edge(u, (v, new)
                messy.prune_edges()  # remove all saturated edges from the graph, and their residual edges

        """

        # graph cache
        debt_cache: flow.FlowGraph = copy.deepcopy(debt_network)

        # create clean graph with the vertices from the current unsimplified graph
        nodes = [v for v in debt_network.graph.keys()]
        simplified_debt = flow.FlowGraph(vertices=nodes)

        # # draw initial graphs
        # debt_network.draw("intra-settle", subdir="test_settle")
        # simplified_debt.draw("simplified", subdir="test_settle", res=False)

        # go through all nodes and their neighbours
        for node in nodes:
            for neighbour in debt_network.neighbours(node):
                # if we request an edge that doesn't exist it has been settled out of the graph
                # so move onto the next pair of nodes
                try:
                    edge = debt_network.get_edge(node, neighbour)
                except flow.EdgeNotFoundError:
                    continue

                # if the max flow between two nodes > 0, add an edge with that max flow to the graph
                if new_flow := MaxFlow.edmunds_karp(debt_network, node, edge.target):
                    simplified_debt.add_edge(
                        edge=flow.Edge(edge.target, 0, new_flow), src=node
                    )

                debt_network.prune_edges()

        if simplified_debt == debt_cache:
            raise NoSimplification("No simplifications were made")

        return simplified_debt
