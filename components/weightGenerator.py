from .energyMixGatherer import gatherEnergyMix
import json

def generateWeights(finalConstraints, prologFacts, deploymentInfo, energyMix):
    # Generate the weights of our constraints
    # Given an average global gco2e consumtpion
    # If our services consume below
    # Give them a malus multiplier
    average_global = 100
    multiplier = 0.75   

    with open(energyMix, "r") as file:
        myEnergyMix = json.load(file)

    def findNode(service, services):
        for s in services:
            if s["service"] == service:
                return s["node"]

    for constr in finalConstraints:
        constr["constraint_emissions"] *= gatherEnergyMix(myEnergyMix, findNode(constr["source"], deploymentInfo))

    maxConsumption = max(constr["constraint_emissions"] for constr in finalConstraints)
  
    for constr in finalConstraints:
        if constr["category"] == "affinity":
            if maxConsumption < average_global:
                final_weight = constr["constraint_emissions"] * multiplier
                final_weight /= average_global
            elif constr["constraint_emissions"] < average_global:
                final_weight = constr["constraint_emissions"] * multiplier
                final_weight /= maxConsumption
            else:
                final_weight = constr["constraint_emissions"] / maxConsumption
            new_rule = f"highConsumptionConnection({constr['source']},{constr["source_flavour"]},{constr['destination']},{constr["destination_flavour"]},{final_weight:.3f})"
            prologFacts.append(new_rule)
        elif constr["category"] == "avoid":
            if maxConsumption < average_global:
                final_weight = constr["constraint_emissions"] * multiplier
                final_weight /= average_global
            elif constr["constraint_emissions"] < average_global:
                final_weight = constr["constraint_emissions"] * multiplier
                final_weight /= maxConsumption
            else:
                final_weight = constr["constraint_emissions"] / maxConsumption
            new_rule = f"highConsumptionService({constr["source"]},{constr["flavour"]},{constr["node"]},{final_weight:.3f})"
            prologFacts.append(new_rule)

    return prologFacts