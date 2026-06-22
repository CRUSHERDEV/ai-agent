import networkx as nx


class IntelligenceGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_relationship(
        self,
        source,
        target,
        relationship
    ):

        self.graph.add_node(source)
        self.graph.add_node(target)

        self.graph.add_edge(
            source,
            target,
            relation=relationship
        )

    def show_relationships(self):

        for u, v, data in self.graph.edges(data=True):

            print(
                f"{u} -> {v} ({data['relation']})"
            )