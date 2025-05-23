import statistics
from collections import defaultdict
import csv
import os
import yaml

class EnergyMixGatherer:
    def __init__(self, path):
        self.path = path

    def gather_energyMix(self, node):
        """Gather the energy mix based on the node."""
        
        # sums = defaultdict(lambda: {"sum": 0.0, "count": 0.0})
        # with open(self.mix, "r") as f:
        #     reader = csv.DictReader(f)
        #     for row in reader:
        #         if row["callback_id"] == "featured_carbon":
        #             key = row["node_id"]
        #             sums[key]["sum"] += float(row["value"])
        #             sums[key]["count"] += 1
        
        with open(self.path, "r") as file:
            myInfra = yaml.safe_load(file)
        myEnergyMix = {
            node: [{"mix": details["profile"]["carbon"]}]
            for node, details in myInfra["nodes"].items()
        }
        
        return statistics.mean(x["mix"] for x in myEnergyMix[node]) #int(sums[self.node]["sum"] / sums[self.node]["count"])