# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './from_3b1b/active/')
from manimlib.imports import *
from sir import DotPerson, SIRSimulation, RunSimpleSimulation, SimpleTravel,Deconf_box


class SIRDeconfSim(SIRSimulation):
    CONFIG={
        "initial_infected_ratio": 0.3,
        "initial_recovered_ratio": 0.1
        }
        # CUSTOM CODE STARTS HERE

        
                

#class RunSimpleDeconfSimulation(SimpleTravel):
#   CONFIG = {
#        "simulation_config": {
#            "person_type": DotPerson,
#            "n_cities": 2,
#            "city_population": 10,
#            "person_config": {
#                "infection_radius": 0.75,
#                "social_distance_factor": 0,
#                "gravity_strength": 0.5,
#            },
#            "travel_rate": 0.02,
#            "infection_time": 5,
#            "initial_infected_ratio": 0.1,
#            "initial_recovered_ratio": 0.7
#        }
#   }

        

    
#class RunSimpleDeconfSimulation(SimpleTravel):
#    CONFIG = {
#        "simulation_config": {
#            "person_type": DotPerson,
#            "n_cities": 2,
#            "city_population": [10,20],
#            "person_config": {
#                "infection_radius": 0.75,
#                "social_distance_factor": 0,
#                "gravity_strength": 0.5,
#            },
#            "travel_rate": 0.02,
#            "infection_time": 5,
#            "initial_infected_ratio": 0.1,
#            "initial_recovered_ratio": 0.7
#        }
#            }
            
class RunSimpleDeconfSimulation(Deconf_box):
    CONFIG = {
#        "initial_infected_ratio": 0.5,
#        "initial_recovered_ratio": 0.7,
        "simulation_config": {
            "person_type": DotPerson,
            "n_cities": 4,
            "city_population": [10,50, 20, 20],
            "person_config": {
                "infection_radius": 0.75,
                "social_distance_factor": 2,
                "gravity_strength": 0.5,
            },
            "travel_rate": 0.01,
            "infection_time": 5,
            }, 
        }

#    def add_simulation(self):
#        self.simulation = SIRDeconfSim(**self.simulation_config)
#        self.add(self.simulation)

class Scenariob(Deconf_box):
    
    CONFIG = {        
        "simulation_config": {
            "initial_infected_ratio": 0.3,
            "initial_recovered_ratio": 0.1,
            "person_type": DotPerson,
            "n_cities": 6,
            "city_population": [30,30, 30, 30, 30, 30],
            "person_config": {
                "infection_radius": 1.5,
                "social_distance_factor": 1,
                "gravity_strength": 0.5,
            },
            "travel_rate": 0.01,
            "infection_time": 5,
            }, 
            "Prop_recovered": 0.2,
        }