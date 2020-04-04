# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './from_3b1b/active/')
from manimlib.imports import *
from sir import DotPerson, SIRSimulation, RunSimpleSimulation


class SIRDeconfSim(SIRSimulation):
    CONFIG={
        "initial_infected_ratio": 0.1,
        "initial_recovered_ratio": 0.1
        }
    
    def add_people(self):
        people = VGroup()
        for box in self.boxes:
            dl_bound = box.get_corner(DL)
            ur_bound = box.get_corner(UR)
            box.people = VGroup()
            for x in range(self.city_population):
                person = self.person_type(
                    dl_bound=dl_bound,
                    ur_bound=ur_bound,
                    **self.person_config
                )
                person.move_to([
                    interpolate(lower, upper, random.random())
                    for lower, upper in zip(dl_bound, ur_bound)
                ])
                person.box = box
                box.people.add(person)
                people.add(person)
                
                
        # CUSTOM CODE STARTS HERE
        num_infected = int(self.initial_infected_ratio * self.city_population * self.n_cities)
        num_recovered = int(self.initial_recovered_ratio * self.city_population * self.n_cities)
        special_status = random.sample(list(people), num_infected + num_recovered)
        
        infected = special_status[:num_infected]
        recovered = special_status[num_infected:]
        
        for person in infected:
            person.set_status("I")
        for person in recovered:
            person.set_status("R")
        self.add(people)
        self.people = people
        

class RunSimpleDeconfSimulation(RunSimpleSimulation):
    CONFIG = {
        "simulation_config": {
            "person_type": DotPerson,
            "initial_infected_ratio": 0.1,
            "initial_recovered_ratio": 0.7
        }
    }

    def add_simulation(self):
        self.simulation = SIRDeconfSim(**self.simulation_config)
        self.add(self.simulation)
