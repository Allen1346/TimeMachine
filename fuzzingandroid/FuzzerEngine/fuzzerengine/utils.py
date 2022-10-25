#!/usr/bin/python
class K_Path_Traveller:

    def __init__(self):
        self.steps = 0
        self.paths = []
        self.path = []

    def get_children(self, node):
        if node == None:
            return None
            print node
        return node.out_nodes

    def travel_DFS(self, graph, node, steps):
        if steps == 1 or len(node.out_nodes) == 0:
            self.path.append(node)
            self.paths.append(self.path[:])
            self.path.pop()
            return

        self.path.append(node)
        children = self.get_children(node)
        for child in children:
            self.travel_DFS(graph, graph.retrieve(child), steps - 1)

        self.path.pop()

    def compute_fitness_k_neighbors(self, graph, node, steps):

        if graph == None or node == None:
            raise Exception('Graph or target node is null')
        if len(graph.states) == 0:
            raise Exception('Graph is empty')
        self.travel_DFS(graph, node, steps)

        return self.paths

    def dump(self, paths):
        for p in self.paths:
            road = ""
            for node in p:
                road = road + node.uid + "-->"
            print "path: " + road
