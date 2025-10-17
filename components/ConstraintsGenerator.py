import json
import yaml
import statistics
import importlib
import inspect

class ConstraintsGenerator:
    def __init__(self, istio, kepler, deployment, infrastructure, application, knowledgeBase, energyMix, activeConstraints):
        self.istio = istio
        self.kepler = kepler
        self.deployment = deployment
        self.infrastructure = infrastructure
        self.application = application
        self.knowledgeBase = knowledgeBase
        self.energyMix = energyMix
        self.activeConstraints = activeConstraints 
        self.maxConsumption = None
        self.prologFacts = None
        with open(self.application, "r") as file:
            self.myapp = yaml.safe_load(file)
        try:
            with open(self.knowledgeBase, "r") as file:
                self.myKnowledgeBase = json.load(file)
        except json.JSONDecodeError:
            self.myKnowledgeBase = {}
        with open(self.activeConstraints, "r") as file:
            self.active = json.load(file)
    
    def generate_constraints(self):
        """From the metrics, sorted from highest consumption to lowest, obtain the constraints to produce in output."""
        
        # Threshold comparator helper function
        def checkThreshold(array, field, threshold):
            output = []
            for var in array:
                if float(var[field] >= threshold):
                    output.append(var)
            return output
        
        # Given a service find which flavour it was deployed as
        def findFlavour(service, services):
            for s in services:
                if s["service"] == service:
                    return s["flavour"]
    
        # Given a service find which node it was deployed on
        def findNode(service, services):
            for s in services:
                if s["service"] == service:
                    return s["node"]

        # Given a service, obtain only the deployable nodes
        def obtainDeployableNodes(service, infrastructure):
            deployableNodes = []
            mynode = findNode(service, self.deployment)
            mysubnet = infrastructure["nodes"][mynode]["capabilities"]["subnet"]
            for node in infrastructure["nodes"]:
                for value in infrastructure["nodes"][node]["capabilities"]:
                    if value == "subnet":
                        if set(mysubnet) & set(infrastructure["nodes"][node]["capabilities"][value]):
                            deployableNodes.append(node)
            return deployableNodes

        # Given a service, obtain the nodes that match its resources
        def obtainResourcefulNodes(service, infrastructure):
            resourcefulNodes = []
            mysecurity = self.myapp["requirements"]["components"][service["service"]]["common"]["security"]
            mycpu = self.myapp["requirements"]["components"][service["service"]]["flavour-specific"][service["flavour"]]["cpu"]
            myram = self.myapp["requirements"]["components"][service["service"]]["flavour-specific"][service["flavour"]]["ram"]
            isDeployable = True
            for node in infrastructure["nodes"]:
                for property in infrastructure["nodes"][node]["capabilities"]:
                    if property == "security":
                        if set(mysecurity) & set(infrastructure["nodes"][node]["capabilities"][property]):
                            isDeployable = True
                        else:
                            isDeployable = False
                    if property == "cpu":
                        if mycpu > infrastructure["nodes"][node]["capabilities"][property]:
                            isDeployable = False
                    if property == "ram":
                        if myram > infrastructure["nodes"][node]["capabilities"][property]:
                            isDeployable = False
                if isDeployable:
                    resourcefulNodes.append(node)
            return resourcefulNodes

        # Find the max consumption for all our estimates
        maxIstio = max(self.istio, key=lambda x: x['emissions'])
        maxKepler = max(self.kepler, key=lambda x: x['emissions'])
        self.maxConsumption = max(maxIstio['emissions'], maxKepler['emissions'])
        #maxNode = max(self.infrastructure["nodes"], key=lambda x: self.energyMix.gather_energyMix(x))

        # Dynamic Thresholding
        cut_points = 100
        threshold_points = 79
        if not self.myKnowledgeBase:
            # Findthe avg consumption for all our estimates
            istioThreshold = statistics.quantiles([x["emissions"] for x in self.istio], n=cut_points)[threshold_points]
            # 80th quantile
            keplerThreshold = statistics.quantiles([x["emissions"] for x in self.kepler], n=cut_points)[threshold_points]
        else:
            quant_istio = []
            for element in self.myKnowledgeBase["connections"]:
                for historyPoint in element["history"]:
                    quant_istio.append((historyPoint["emissions"] / historyPoint["count"]))
            for element in self.istio:
                quant_istio.append(element["emissions"])
            istioThreshold = statistics.quantiles(quant_istio, n=cut_points)[threshold_points]
            # 80th quantile
            quant_kepler = []
            for element in self.myKnowledgeBase["services"]:
                for historyPoint in element["history"]:
                    quant_kepler.append((historyPoint["emissions"] / historyPoint["count"]))
            for element in self.kepler:
                quant_kepler.append(element["emissions"])
            keplerThreshold = statistics.quantiles(quant_kepler, n=cut_points)[threshold_points]
        
        self.prologFacts = []

        # Prolog file preparation
        # For each communication in our Istio metrics, save the fact
        for comm in self.istio:
            fact = f'serviceConnection({comm["source"]}, {comm["destination"]}, {comm["emissions"]}, {comm["joules"]})'
            self.prologFacts.append(fact)
        # For each service in our Kepler metrics, save the fact    
        for service in self.kepler:
            fact = f'service({service["service"]}, {service["emissions"]}, {service["joules"]})'
            self.prologFacts.append(fact)
        # For each node in our infrastructure, save the fact
        for node in self.infrastructure["nodes"]:
            fact = f'node({node}, {self.infrastructure["nodes"][node]["profile"]["carbon"]})'
            self.prologFacts.append(fact)
        # For each element in our deployment, save the fact
        for element in self.deployment:
            rule = f'deployedTo({element["service"]},{element["flavour"]},{element["node"]})'
            self.prologFacts.append(rule)

        active_constraints = []
        generated_constraints = []
        thresholds = []  
        
        for item in self.active:
            if item["active"]:
                module_name = item["module"]
                module_path = f"components.constraints.{module_name}"
                module = importlib.import_module(module_path)
                cls = getattr(module, module_name)
                instance = cls()
                active_constraints.append(instance)

        available_thresholds = {
            "istioThreshold": istioThreshold,
            "keplerThreshold": keplerThreshold
        }

        for constr in active_constraints:
            if hasattr(constr, "get_neededThreshold"):
                needed = constr.get_neededThreshold()
                for name in needed:
                    if name in available_thresholds:
                        thresholds.append(available_thresholds[name])

        # Filter only the consumption above the threshold, which are to our interest
        maxThreshold = max(thresholds)
        monitorIstio = sorted(checkThreshold(self.istio, 'emissions', maxThreshold), key=lambda x: x['emissions'], reverse=True)
        monitorKepler = sorted(checkThreshold(self.kepler, 'emissions', maxThreshold), key=lambda x: x['emissions'], reverse=True)

        available_args = {
            "deployment": self.deployment,
            "infrastructure": self.infrastructure,
            "monitorIstio": monitorIstio,
            "energyMix": self.energyMix,
            "myapp": self.myapp,
            "maxThreshold": maxThreshold,
            "monitorKepler": monitorKepler,
            "kepler": self.kepler
        }

        for constr in active_constraints:
            method = getattr(constr, "generate_constraints")
            sig = inspect.signature(method)
            args_to_pass = {
                name: available_args[name]
                for name in sig.parameters
                if name in available_args
            }
            generated_constraints += method(**args_to_pass)
        
        return generated_constraints, self.prologFacts