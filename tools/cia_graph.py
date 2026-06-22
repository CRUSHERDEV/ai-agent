import time

class CIAGraph:
    def __init__(self):
        self.nodes = {}
        self.links = []
        self.history = []

    # =====================
    # NODE SYSTEM
    # =====================
    def add_node(self, name, value=0):
        self.nodes[name] = {
            "name": name,
            "value": value,
            "updated_at": time.time()
        }

    def update_node(self, name, value):
        if name in self.nodes:
            self.nodes[name]["value"] = value
            self.nodes[name]["updated_at"] = time.time()
        else:
            self.add_node(name, value)

    # =====================
    # LINK SYSTEM
    # =====================
    def add_link(self, source, target, strength):
        self.links.append({
            "source": source,
            "target": target,
            "strength": strength,
            "timestamp": time.time()
        })

    # =====================
    # SNAPSHOT
    # =====================
    def snapshot(self):
        return {
            "nodes": list(self.nodes.values()),
            "links": self.links
        }

    # =====================
    # MEMORY LOG
    # =====================
    def log(self, event):
        self.history.append({
            "event": event,
            "time": time.time()
        })


# GLOBAL GRAPH INSTANCE
graph = CIAGraph()