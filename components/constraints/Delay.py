from datetime import datetime

class Delay:
    def __init__(self):
        self.delayConstraints = []

    def generate_constraints(self, deployment, myapp, energyMix, kepler):
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

        for service in myapp["requirements"]["components"]:
            keywords = myapp["requirements"]["components"][service].get("common", {})
            # Consult energyMix to calculate when would it be best to deploy
            if "delay" in keywords:
                # Find the node where our service is deployed to
                node = findNode(service, deployment)
                # Obtain the behaviour of the node in the following *delay* hours
                node_behaviour = energyMix.gather_future()
                current_hour = datetime.now().strftime("%H")
                hours_ahead = keywords["delay"]

                result = {}
                for i in range(hours_ahead+1):
                    hour = (int(current_hour) + i) % 24
                    hour_str = f"{hour:02d}"
                    if hour_str in node_behaviour["nodes"][node]:
                        result[hour_str] = node_behaviour["nodes"][node][hour_str]
                delay_hr, _ = min(
                    result.items(),
                    key=lambda item: item[1]["mix"]
                )
                
                sum_avoided_mixes = 0
                count_avoided_mixes = 0
                for hour_string, data in result.items():
                    if hour_string == delay_hr:
                        break
                    sum_avoided_mixes += data["mix"]
                    count_avoided_mixes += 1
                for item in kepler:
                    if item["service"] == service:
                        emiss = item["emissions"]
                        break
                
                delay = {
                    "category": "delay",
                    "source": service,
                    "flavour": findFlavour(service, deployment),
                    "delay": count_avoided_mixes,
                    "constraint_emissions": emiss * (sum_avoided_mixes / count_avoided_mixes)
                }
                self.delayConstraints.append(delay)

        return self.delayConstraints