import json
import re

class WeightGenerator:
    def __init__(self, constraints, prologFacts, deployment, activeConstraints):
        self.constraints = constraints
        self.prologFacts = prologFacts
        self.deployment = deployment
        self.activeConstraints = activeConstraints 
        self.contraints_threshold = 0.1 
        self.average_global = 100
        self.multiplier = 0.75
        with open(self.activeConstraints, "r") as file:
            self.active = json.load(file)

    def generate_weights(self):
        """
        Generate the weights of our constraints given an average global gco2e consumtpion if our services consume below
        give them a malus multiplier
        """

        maxConsumption = max(
            constr["constraint_emissions"]
            for constr in self.constraints
            if "constraint_emissions" in constr
        )
        
        category_to_template = {
            item["module"].lower(): item["template"]
            for item in self.active
            if item["active"]
        }
        for constr in self.constraints:
            category = constr.get("category")
            template = category_to_template.get(category)

            if "constraint_emissions" in constr:
                # Weight calculation
                ce = constr["constraint_emissions"]
                if maxConsumption < self.average_global:
                    final_weight = ce * self.multiplier / self.average_global
                elif ce < self.average_global:
                    final_weight = ce * self.multiplier / maxConsumption
                else:
                    final_weight = ce / maxConsumption
                try:
                    new_rule = template.format(**constr, weight=final_weight)
                    self.prologFacts.append(new_rule)
                except KeyError as e:
                    print(f"Missing key for category '{category}': {e}")
            else:
                try:
                    new_rule = template.format(**constr)
                    self.prologFacts.append(new_rule)
                except KeyError as e:
                    print(f"Missing key for category '{category}': {e}")

        itemsToRemove = []
        for fact in self.prologFacts:
            if fact.startswith("high"):
                match = re.match(r'(\w+)\((.*?)\)', fact)
                if match:
                    args = match.group(2).split(',')
                    if float(args[-1]) < self.contraints_threshold:
                        itemsToRemove.append(fact)
        for fact in itemsToRemove:
            self.prologFacts.remove(fact)
            
        return self.prologFacts