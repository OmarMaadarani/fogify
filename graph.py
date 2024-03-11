import docker
import networkx as nx
from typing import List, Dict
from pydantic import BaseModel, Field, AliasPath, TypeAdapter
import matplotlib
import matplotlib.pyplot as plt

#matplotlib.use('Agg')

class FogNetwork(BaseModel):
	Name: str
	Id: str
	Subnet: str = Field(validation_alias=AliasPath("IPAM", "Config", 0, "Subnet"))

	def __hash__(self) -> int:
		return self.Id.__hash__()
	
	def __repr__(self):
		return self.Name


class FogContainer(BaseModel):
	Id: str
	Name: str
	Networks: List[FogNetwork]

	def __hash__(self) -> int:
		return self.Id.__hash__()
	
	def __repr__(self):
		return self.Name
	

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

def nodeAttrs(G: nx.Graph):
	"""
	Dynamically changes attributes of nodes based on whether the node represents Container or a Network
	"""
	for node in G.nodes():
		G.nodes[node]["shape"] 

	return

def drawTopology():
	G = nx.Graph()
	#G.add_edges_from(edgeList)
	#print(G.edges())
	G.add_nodes_from(topoNetworks, Type='NETWORK')
	G.add_nodes_from(fogifyCntrs, Type='CONTAINER')
	G.add_edges_from(edgeList)
	print(G.nodes())

	pos = nx.spring_layout(G)
	#nx.draw_networkx_edges(G, pos, edgeList)
	nx.draw_networkx(G, pos, nodelist=topoNetworks, node_color="#ff5252", node_shape="^")
	nx.draw_networkx(G, pos, nodelist=fogifyCntrs)
	#nx.draw_networkx_nodes(G, pos, topoNetworks, node_color="#ff5252", node_shape="^")
	#nx.draw_networkx_nodes(G, pos, fogifyCntrs)
	#nx.draw(G, with_labels=True)
	plt.show()

fogifyCntrs = containerList()
# Create Unique List (Set) of networks used in the Topology (i.e Get unique networks used from each container in topology)
topoNetworks = set(net for cntr in fogifyCntrs for net in cntr.Networks)
edgeList = buildEdges()

drawTopology()




