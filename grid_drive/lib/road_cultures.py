from grid_drive.lib.culture_lib.culture import Culture, Argument
from grid_drive.lib.road_cell import RoadCell
from grid_drive.lib.road_agent import RoadAgent
import numpy as np
import copy

#####################
# EASY ROAD CULTURE #
#####################

class RoadCulture(Culture):
	starting_argument_id = 0

	def __init__(self, np_random=None):
		self.np_random = np.random if np_random is None else np_random
		super().__init__()

	def initialise_random_agent(self, agent: RoadAgent):
		"""
		Receives an empty RoadAgent and initialises properties with acceptable random values.
		:param agent: uninitialised RoadAgent.
		"""
		agent.assign_property_value("Speed", 0)

	def initialise_feasible_road(self, road: RoadCell):
		for p in self.properties.keys():
			road.assign_property_value(p, False)

	def run_default_dialogue(self, road, agent, explanation_type="verbose"):
		"""
		Runs dialogue to find out decision regarding penalty in argumentation framework.
		Args:
			road: RoadCell corresponding to destination cell.
			agent: RoadAgent corresponding to agent.
			explanation_type: 'verbose' for all arguments used in exchange; 'compact' for only winning ones.

		Returns: Decision on penalty + explanation.
		"""
		# Game starts with proponent using argument 0 ("I will not get a ticket").
		return super().run_dialogue(road, agent, starting_argument_id=self.starting_argument_id, explanation_type=explanation_type)

	def get_minimum_speed(self, road, agent):
		agent = copy.deepcopy(agent)
		for speed in [0,10,20,30,40]:
			agent.assign_property_value("Speed", speed)
			can_move, _ = self.run_default_dialogue(road, agent, explanation_type="compact")
			if can_move:
				return speed
		return None

	def get_speed_limits(self, road, agent):
		agent = copy.deepcopy(agent)
		min_speed = self.get_minimum_speed(road, agent)
		if min_speed is None:
			return (None,None) # (None,None) if road is unfeasible
		max_speed = None
		step = 10
		for speed in range(min_speed+step, self.agent_options.get('speed',120)+1, step):
			agent.assign_property_value("Speed", speed)
			can_move, _ = self.run_default_dialogue(road, agent, explanation_type="compact")
			if can_move:
				if max_speed is None or speed > max_speed:
					max_speed = speed
		if max_speed is None:
			max_speed = min_speed
		return (min_speed, max_speed)

class EasyRoadCulture(RoadCulture):
	def __init__(self, road_options=None, agent_options=None, np_random=None):
		if road_options is None: road_options = {}
		if agent_options is None: agent_options = {}
		self.road_options = road_options
		self.agent_options = agent_options
		self.ids = {}
		super().__init__(np_random)
		self.name = "Easy Road Culture"
		# Properties of the culture with their default values go in self.properties.
		self.properties = {
			"Motorway": False,
			"Stop Sign": False
		}
		self.agent_properties = {"Speed": 0}

	def create_arguments(self):
		"""
		Defines set of arguments present in the culture and their verifier functions.
		"""
		def build_argument(_id, _label, _description, _verifier_fn):
			motion = Argument(_id, _description)
			self.ids[_label] = _id
			motion.set_verifier(_verifier_fn)  # Propositional arguments are always valid.
			return motion
		self.AF.add_arguments([
			build_argument(0, "ok", "Nothing wrong.", lambda *gen: True), # Propositional arguments are always valid.
			build_argument(1, "is_motorway", "This is a motorway.", lambda road, agent: road["Motorway"] is True),
			build_argument(2, "has_stop_sign", "There is a stop sign.", lambda road, agent: road["Stop Sign"] is True),
			build_argument(3, "speed==0", "My speed is 0.", lambda road, agent: agent["Speed"] <= 0),
			build_argument(4, "speed<=70", "My speed is 70 or less.", lambda road, agent: agent["Speed"] <= 70),
		])

	def initialise_random_road(self, road: RoadCell):
		"""
		Receives an empty RoadCell and initialises properties with acceptable random values.
		:param road: uninitialised RoadCell.
		"""
		motorway = self.np_random.random() <= self.road_options.get('motorway',1/2)
		road.assign_property_value("Motorway", motorway)
		if motorway:
			road.assign_property_value("Stop Sign", False)
		else:
			road.assign_property_value("Stop Sign", self.np_random.random() <= self.road_options.get('stop_sign',1/2))

	def define_attacks(self):
		"""
		Defines attack relationships present in the culture.
		"""
		ID = self.ids

		self.AF.add_attack(ID["is_motorway"], ID["ok"])
		self.AF.add_attack(ID["has_stop_sign"], ID["ok"])
		self.AF.add_attack(ID["has_stop_sign"], ID["is_motorway"])
		self.AF.add_attack(ID["speed==0"], ID["has_stop_sign"])
		self.AF.add_attack(ID["speed<=70"], ID["is_motorway"])

#######################
# MEDIUM ROAD CULTURE #
#######################

class MediumRoadCulture(RoadCulture):
	def __init__(self, road_options=None, agent_options=None, np_random=None):
		if road_options is None: road_options = {}
		if agent_options is None: agent_options = {}
		self.road_options = road_options
		self.agent_options = agent_options
		self.ids = {}
		super().__init__(np_random)
		self.name = "Medium Road Culture"
		# Properties of the culture with their default values go in self.properties.
		self.properties = {
			"Motorway": False,
			"Stop Sign": False,
			"School": False,
			"Single Lane": False,
			"Town Road": False
		}

		self.agent_properties = {
			"Speed": 0,
			"Emergency Vehicle": False
		}

	def create_arguments(self):
		"""
		Defines set of arguments present in the culture and their verifier functions.
		"""
		def build_argument(_id, _label, _description, _verifier_fn):
			motion = Argument(_id, _description)
			self.ids[_label] = _id
			motion.set_verifier(_verifier_fn)  # Propositional arguments are always valid.
			return motion
		self.AF.add_arguments([
			build_argument(0, "ok", "Nothing wrong.", lambda *gen: True), # Propositional arguments are always valid.
			build_argument(1, "is_motorway", "This is a motorway.", lambda road, agent: road["Motorway"] is True),
			build_argument(2, "has_stop_sign", "There is a stop sign.", lambda road, agent: road["Stop Sign"] is True),
			build_argument(3, "has_school", "There is a school nearby.", lambda road, agent: road["School"] is True),
			build_argument(4, "single_lane", "This is a single lane road.", lambda road, agent: road["Single Lane"] is True),
			build_argument(5, "town_road", "This is a town road.", lambda road, agent: road["Town Road"] is True),
			build_argument(6, "speed==0", "My speed is 0.", lambda road, agent: agent["Speed"] <= 0),
			build_argument(7, "speed<=20", "My speed is 20 or less.", lambda road, agent: agent["Speed"] <= 20),
			build_argument(8, "speed<=30", "My speed is 30 or less.", lambda road, agent: agent["Speed"] <= 30),
			build_argument(9, "speed<=60", "My speed is 60 or less.", lambda road, agent: agent["Speed"] <= 60),
			build_argument(10, "speed<=70", "My speed is 70 or less.", lambda road, agent: agent["Speed"] <= 70),
			build_argument(11, "emergency_vehicle", "I am an emergency vehicle.", lambda road, agent: agent["Emergency Vehicle"] is True),
		])

	def initialise_random_road(self, road: RoadCell):
		"""
		Receives an empty RoadCell and initialises properties with acceptable random values.
		:param road: uninitialised RoadCell.
		"""
		motorway = True if self.np_random.random() <= self.road_options.get('motorway',1/2) else False
		road.assign_property_value("Motorway", motorway)
		if motorway:
			road.assign_property_value("School", False)
			road.assign_property_value("Town Road", False)
			road.assign_property_value("Stop Sign", False)
		else:
			road.assign_property_value("Stop Sign", self.np_random.random() <= self.road_options.get('stop_sign',1/2))
			road.assign_property_value("School", self.np_random.random() <= self.road_options.get('school',1/2))
			road.assign_property_value("Town Road", self.np_random.random() <= self.road_options.get('town_road',1/2))
		road.assign_property_value("Single Lane", self.np_random.random() <= self.road_options.get('single_lane',1/2))

	def initialise_random_agent(self, agent: RoadAgent):
		"""
		Receives an empty RoadAgent and initialises properties with acceptable random values.
		:param agent: uninitialised RoadAgent.
		"""
		agent.assign_property_value("Emergency Vehicle", self.np_random.random() <= self.agent_options.get('emergency_vehicle',1/5))
		super().initialise_random_agent(agent)

	def define_attacks(self):
		"""
		Defines attack relationships present in the culture.
		"""
		ID = self.ids

		# Base conditions for ticket.
		self.AF.add_attack(ID["is_motorway"], ID["ok"])
		self.AF.add_attack(ID["has_stop_sign"], ID["ok"])
		self.AF.add_attack(ID["has_school"], ID["ok"])
		self.AF.add_attack(ID["single_lane"], ID["ok"])
		self.AF.add_attack(ID["town_road"], ID["ok"])

		# Speed checks and mitigatory rules.
		self.AF.add_attack(ID["speed==0"], ID["has_stop_sign"])
		self.AF.add_attack(ID["speed<=20"], ID["has_school"])
		self.AF.add_attack(ID["speed<=30"], ID["town_road"])
		self.AF.add_attack(ID["speed<=60"], ID["single_lane"])
		self.AF.add_attack(ID["speed<=70"], ID["is_motorway"])

		self.AF.add_attack(ID["emergency_vehicle"], ID["has_stop_sign"])
		self.AF.add_attack(ID["emergency_vehicle"], ID["has_school"])
		self.AF.add_attack(ID["emergency_vehicle"], ID["town_road"])
		self.AF.add_attack(ID["emergency_vehicle"], ID["single_lane"])
		self.AF.add_attack(ID["emergency_vehicle"], ID["is_motorway"])

#####################
# HARD ROAD CULTURE #
#####################

class HardRoadCulture(RoadCulture):
	def __init__(self, road_options=None, agent_options=None, np_random=None):
		if road_options is None: road_options = {}
		if agent_options is None: agent_options = {}
		self.road_options = road_options
		self.agent_options = agent_options
		self.ids = {}
		super().__init__(np_random)
		self.name = "Hard Road Culture"
		# Properties of the culture with their default values go in self.properties.
		self.properties = {
			"Motorway": False,
			"Stop Sign": False,
			"School": False,
			"Single Lane": False,
			"Town Road": False,
			"Roadworks": False,
			"Accident": False,
			"Heavy Rain": False,
			"Congestion Charge": False
		}

		self.agent_properties = {
			"Speed": 0,
			"Emergency Vehicle": False,
			"Heavy Vehicle": False,
			"Worker Vehicle": False,
			"Tasked": False,
			"Paid Charge": False
		}

	def create_arguments(self):
		"""
		Defines set of arguments present in the culture and their verifier functions.
		"""
		def build_argument(_id, _label, _description, _verifier_fn):
			motion = Argument(_id, _description)
			self.ids[_label] = _id
			motion.set_verifier(_verifier_fn)  # Propositional arguments are always valid.
			return motion
		self.AF.add_arguments([
			build_argument(0, "ok", "Nothing wrong.", lambda *gen: True), # Propositional arguments are always valid.
			build_argument(1, "motorway_above_70", "You are driving on a motorway with speed above 70.", lambda road, agent: road["Motorway"] is True and agent["Speed"] > 70),
			build_argument(2, "emergency_vehicle", "You are an emergency vehicle.", lambda road, agent: agent["Emergency Vehicle"] is True),
			build_argument(3, "tasked_emergency_vehicle", "You are a tasked emergency vehicle.", lambda road, agent: agent["Emergency Vehicle"] is True and agent["Tasked"] is True),
			build_argument(4, "motorway_below_30", "You are driving on a motorway with speed below 30.", lambda road, agent: road["Motorway"] is True and agent["Speed"] <= 30),
			build_argument(5, "accident", "There is an accident ahead.", lambda road, agent: road["Accident"] is True),
			build_argument(6, "stop_sign", "There is a stop sign ahead.", lambda road, agent: road["Accident"] is True),
			build_argument(7, "single_lane_above_60", "You are driving on a single lane road with speed above 60.", lambda road, agent: road["Single Lane"] is True and agent["Speed"] > 60),
			build_argument(8, "town_road_above_30", "You are driving on a town road with speed above 30.", lambda road, agent: road["Town Road"] is True and agent["Speed"] > 30),
			build_argument(9, "school_road_above_20", "You are driving on a school road with speed above 20.", lambda road, agent: road["School"] is True and agent["Speed"] > 20),
			build_argument(10, "roadworks", "You drove into roadworks.", lambda road, agent: road["Roadworks"] is True),
			build_argument(11, "worker_below_30", "You are a worker vehicle driving with speed below 30.", lambda road, agent: agent["Worker Vehicle"] is True and agent["Speed"] <= 30 and agent["Tasked"] is True),
			build_argument(12, "stop_sign_above_0", "There is a stop sign and your speed is above 0.", lambda road, agent: road["Stop Sign"] is True and agent["Speed"] > 0),
			build_argument(13, "accident_below_20", "There is an accident and your speed is below 20.", lambda road, agent: road["Accident"] is True and agent["Speed"] <= 20),
			build_argument(14, "heavy_above_50", "You are driving a heavy vehicle at speed above 50.", lambda road, agent: agent["Heavy Vehicle"] is True and agent["Speed"] > 50),
			build_argument(15, "rain_above_60", "It is raining heavily and your speed is above 60.", lambda road, agent: road["Heavy Rain"] is True and agent["Speed"] > 60),
			build_argument(16, "congestion_charge_not_paid", "There is a congestion charge which hasn't been paid.", lambda road, agent: road["Congestion Charge"] is True and agent["Paid Charge"] is False),
			build_argument(17, "heavy_rain", "It is raining heavily.", lambda road, agent: road["Heavy Rain"] is True),
			build_argument(18, "heavy_vehicle", "I am a heavy vehicle.", lambda road, agent: agent["Heavy Vehicle"] is True),
			build_argument(19, "worker_vehicle", "I am a worker vehicle.", lambda road, agent: agent["Worker Vehicle"] is True),
		])

	def initialise_random_road(self, road: RoadCell):
		"""
		Receives an empty RoadCell and initialises properties with acceptable random values.
		:param road: uninitialised RoadCell.
		"""
		motorway = self.np_random.random() <= self.road_options.get('motorway',1/2)
		road.assign_property_value("Motorway", motorway)

		if motorway:
			road.assign_property_value("School", False)
			road.assign_property_value("Town Road", False)
			road.assign_property_value("Stop Sign", False)
		else:
			road.assign_property_value("School", self.np_random.random() <= self.road_options.get('school',1/2))
			road.assign_property_value("Town Road", self.np_random.random() <= self.road_options.get('town_road',1/2))
			road.assign_property_value("Stop Sign", self.np_random.random() <= self.road_options.get('stop_sign',1/2))

		road.assign_property_value("Single Lane", self.np_random.random() <= self.road_options.get('single_lane',1/2))
		road.assign_property_value("Roadworks", self.np_random.random() <= self.road_options.get('roadworks',1/2))
		road.assign_property_value("Accident", self.np_random.random() <= self.road_options.get('accident',1/8))
		road.assign_property_value("Heavy Rain", self.np_random.random() <= self.road_options.get('heavy_rain',1/2))
		road.assign_property_value("Congestion Charge", self.np_random.random() <= self.road_options.get('congestion_charge',1/2))

	def initialise_random_agent(self, agent: RoadAgent):
		"""
		Receives an empty RoadAgent and initialises properties with acceptable random values.
		:param agent: uninitialised RoadAgent.
		"""
		agent.assign_property_value("Emergency Vehicle", self.np_random.random() <= self.agent_options.get('emergency_vehicle',1/5))
		agent.assign_property_value("Heavy Vehicle", self.np_random.random() <= self.agent_options.get('heavy_vehicle',1/4))
		agent.assign_property_value("Worker Vehicle", self.np_random.random() <= self.agent_options.get('worker_vehicle',1/3))
		agent.assign_property_value("Tasked", self.np_random.random() <= self.agent_options.get('tasked',1/2))
		agent.assign_property_value("Paid Charge", self.np_random.random() <= self.agent_options.get('paid_charge',1/2))

		super().initialise_random_agent(agent)

	def define_attacks(self):
		"""
		Defines attack relationships present in the culture.
		Culture can be seen here:
		https://docs.google.com/document/d/1O7LCeRVVyCFnP-_8PVcfNrEdVEN5itGxcH1Ku6GN5MQ/edit?usp=sharing
		"""
		ID = self.ids

		# 1
		self.AF.add_attack(ID["motorway_above_70"], ID["ok"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["motorway_above_70"])

		# 2
		self.AF.add_attack(ID["motorway_below_30"], ID["ok"])
		self.AF.add_attack(ID["heavy_vehicle"], ID["motorway_below_30"])
		self.AF.add_attack(ID["accident"], ID["motorway_below_30"])
		self.AF.add_attack(ID["stop_sign"], ID["motorway_below_30"])

		# 3
		self.AF.add_attack(ID["single_lane_above_60"], ID["ok"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["single_lane_above_60"])

		# 4
		self.AF.add_attack(ID["town_road_above_30"], ID["ok"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["town_road_above_30"])

		# 5
		self.AF.add_attack(ID["school_road_above_20"], ID["ok"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["school_road_above_20"])

		# 6
		self.AF.add_attack(ID["stop_sign_above_0"], ID["ok"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["stop_sign_above_0"])

		# 7
		self.AF.add_attack(ID["accident_below_20"], ID["ok"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["accident_below_20"])
		self.AF.add_attack(ID["stop_sign_above_0"], ID["accident_below_20"])
		
		# 8
		self.AF.add_attack(ID["heavy_above_50"], ID["ok"])
		
		# 9
		self.AF.add_attack(ID["rain_above_60"], ID["ok"])

		# 10
		self.AF.add_attack(ID["congestion_charge_not_paid"], ID["ok"])
		self.AF.add_attack(ID["emergency_vehicle"], ID["congestion_charge_not_paid"])
		self.AF.add_attack(ID["worker_vehicle"], ID["congestion_charge_not_paid"])
		self.AF.add_attack(ID["heavy_rain"], ID["congestion_charge_not_paid"])

		# 11
		self.AF.add_attack(ID["roadworks"], ID["ok"])
		self.AF.add_attack(ID["worker_below_30"], ID["roadworks"])
		self.AF.add_attack(ID["tasked_emergency_vehicle"], ID["roadworks"])

