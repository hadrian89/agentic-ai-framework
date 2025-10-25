import json
import uuid

class GraphBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node_type, label):
        node_id = str(uuid.uuid4())
        self.nodes.append({"id": node_id, "type": node_type, "label": label})
        return node_id

    def add_edge(self, source, target):
        self.edges.append({"from": source, "to": target})

    def build_from_plan(self, plan):
        """Convert plan steps into JSON graph structure"""
        prev_node = None
        for step in plan["steps"]:
            node_id = self.add_node("ExecutionNode", step)
            if prev_node:
                self.add_edge(prev_node, node_id)
            prev_node = node_id
        return self.to_json()

    def to_json(self):
        return json.dumps({"nodes": self.nodes, "edges": self.edges}, indent=2)
