from pyswip import Prolog
import yaml
import os

class Adapter:
    def __init__(self, prologRules, prologFile, prologFacts, prologOutput, constraints, explanationFile, yamlOut, infrastructure, energyMix):
        self.prologRules = prologRules
        self.prologFile = prologFile
        self.prologFacts = prologFacts
        self.constraints = constraints
        self.prologOutput = prologOutput
        self.explanationFile = explanationFile
        self.yamlout = yamlOut
        self.infrastructure = infrastructure
        self.energyMix = energyMix
        self.contraints_threshold = 0.1 
        self.nodes = []
        for node in self.infrastructure["nodes"]:
            details = {"node": node,
                        "carbon": self.infrastructure["nodes"][node]["profile"]["carbon"]}
            self.nodes.append(details)
        self.minNode = min(self.infrastructure["nodes"], key=lambda x: self.energyMix.gather_energyMix(x))
        self.nodes = sorted(self.nodes, key=lambda x: x['carbon'], reverse=True)

    # Create the prolog file and execute it
    def adapt_output(self):
        """Adapts to the correct format the output."""
        def explain(constrType):
            match constrType:
                case "affinity":
                    return "since the services exchanged a lot of data between them"
                case "avoidNode":
                    return "This decision was driven by the high resource consumption of the selected flavour combined with the poor energy mix of the target node."
                case "delay":
                    return "This service is not mandatory for the initial deployment and so its deployment can be delayed"

        def savings(constraint):
            def obtainIndex(data, element):
                index = next(i for i, item in enumerate(data) if item["node"] == element)
                return index
            index = min(obtainIndex(self.nodes, constraint["node"]), len(self.nodes))
            maxSave = constraint["constraint_emissions"] - (constraint["constraint_emissions"] / self.nodes[index]["carbon"] * self.infrastructure["nodes"][self.minNode]["profile"]["carbon"])
            try:
                minSave = constraint["constraint_emissions"] - (constraint["constraint_emissions"] / int(self.nodes[index]["carbon"]) * int(self.nodes[index+1]["carbon"]))
            except IndexError:
                minSave = maxSave
            return f"The estimated emissions savings resulting from avoiding this deployment range between {maxSave} gCO2eq and {minSave} gCO2eq."

        with open(self.prologFile, 'w') as file:
            for fact in self.prologFacts:
                file.write(fact + ".\n")

        p = Prolog()
        p.consult(self.prologRules)
        list(p.query(f"save_to_file(['{self.prologFile}', '{self.prologOutput}'])"))
        # Prolog().consult("rules2.pl")

        maxV = max(x["constraint_emissions"] for x in self.constraints if "constraint_emissions" in x)
        
        final_explanation = []
        for constraint in self.constraints:
            if "constraint_emissions" in constraint:
                if (constraint.get("constraint_emissions") / maxV) > self.contraints_threshold:
                    if constraint["category"] == "affinity":
                        explanation = (f'A {constraint["category"]} was generated '
                            f'between {constraint["source"]} in flavour {constraint["source_flavour"]} '
                            f'and {constraint["destination"]} in flavour {constraint["destination_flavour"]} '
                            f'{explain(constraint["category"])}\n')
                        final_explanation.append(explanation)
                    elif constraint["category"] == "avoid":
                        constraint["category"] = "avoidNode"
                        explanation = (f'A {constraint["category"]} constraint was generated '
                            f'for the deployment of the {constraint["source"]} component in the {constraint["flavour"]} flavour '
                            f'on the {constraint["node"]} node. {explain(constraint["category"])}\n'
                            f'{savings(constraint)}\n'
                            )
                        final_explanation.append(explanation)
        with open(self.explanationFile, "w") as explfile:
            explfile.write("\n".join(final_explanation))

        outputdata = {
            "requirements": {
                "components": {}
            }
        }
        for element in self.constraints:
            if "constraint_emissions" in element:
                if (element.get("constraint_emissions") / maxV) > 0.3:
                    source = element["source"]
                    flavour = element.get("source_flavour", element.get("flavour", None))
                    affinityvalue = element.get("destination", element.get("delay", None)) #+ "," + element.get("destination_flavour", "")
                    
                    if source not in outputdata["requirements"]["components"]:
                        outputdata["requirements"]["components"][source] = {}
                    if flavour not in outputdata["requirements"]["components"][source]:
                        outputdata["requirements"]["components"][source][flavour] = []

                    outputdata["requirements"]["components"][source][flavour].append({
                        element.get("category"): {
                            "energy_oriented": True,
                            "resilience_oriented": False,
                            "soft": True,
                            "value": element.get("node", affinityvalue)
                        }
                    })
            else:
                source = element["source"]
                flavour = element.get("source_flavour", element.get("flavour", None))

                if source not in outputdata["requirements"]["components"]:
                    outputdata["requirements"]["components"][source] = {}
                if flavour not in outputdata["requirements"]["components"][source]:
                    outputdata["requirements"]["components"][source][flavour] = []
                    
                outputdata["requirements"]["components"][source][flavour].append({
                    element.get("category"): {
                        "energy_oriented": True,
                        "resilience_oriented": False,
                        "soft": True,
                        "value": element.get("delay")
                    }
                })


        with open(self.yamlout, "w") as file:
            yaml.dump(outputdata, file, default_flow_style=False)