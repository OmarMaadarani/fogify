import docker
import networkx as nx
from typing import List, Dict
from pydantic import BaseModel, Field, AliasPath, TypeAdapter
import matplotlib.pyplot as plt

class FogNetwork(BaseModel):
	Name: str
	Id: str
	Subnet: str = Field(validation_alias=AliasPath("IPAM", "Config", 0, "Subnet"))

	def __hash__(self) -> int:
		return self.Id.__hash__()

	def __str__(self):
		return f"ID: {self.id}, Name: {self.name}, Subnet: {self.subnet}"

class FogContainer(BaseModel):
	Id: str
	Name: str
	Networks: List[FogNetwork]

	def toString(self):
		return f"ID: {self.id}, Name: {self.name}, Networks: {self.networks}"


client = docker.from_env()

def containerList() -> List[FogContainer]:
	containers = []
	for cntr in client.containers.list():
		cntr_stack = cntr.labels.get("com.docker.stack.namespace")
		if(cntr_stack == "fogify"):
			cntr_nets = getNetworks(cntr.attrs.get("NetworkSettings").get("Networks").items())
			#print(cntr_nets)
			containers.append(FogContainer.model_validate({**cntr.attrs, "Networks": cntr_nets}))
	
	return containers

def getNetworks(nets: tuple) -> List[FogNetwork]:
	"""
	Method to get Networks from the Fogify Topology
	"""
	netList = []
	for net, info in nets:
		if(net == "ingress"): continue

		fogNet = FogNetwork.model_validate(client.networks.get(info['NetworkID']).attrs)
		netList.append(fogNet)
	
	return netList

def buildEdges():
	edgeList = []

	for net in topoNetworks:
		for cntr in fogifyCntrs:
			if (cntr.Networks.count(net) != 0):
				edgeList.append( (net.Name, cntr.Name) )
				continue
	
	return edgeList	

fogifyCntrs = containerList()
# Create Unique List (Set) of networks used in the Topology (i.e Get unique networks used from each container in topology)
topoNetworks = set(net for cntr in fogifyCntrs for net in cntr.Networks)

edgeList = buildEdges()
print(edgeList)

G = nx.Graph()
G.add_edges_from(edgeList)
nx.draw_spring(G, with_labels=True)
plt.show()

