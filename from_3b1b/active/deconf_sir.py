# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './from_3b1b/active/')
from manimlib.imports import *
from sir import Person, SIRSimulation, RunSimpleSimulation

class DotPerson(Person):
    def get_body(self):
        return Dot()

class SquarePerson(Person):
    def get_body(self):
        return Square()
    
class TrianglePerson(Person):
    def get_body(self):
        return Triangle()
    

class RespectfulCitizen(DotPerson):
    CONFIG = {
        "social_distance_factor": 1
        }
    
class DisrespectfulCitizen(TrianglePerson):
    CONFIG = {
        "social_distance_factor": 0
        }
    

class MultiPopSIRSimulation(SIRSimulation):
    CONFIG = {
        "n_cities": 1,
        "city_population": 100,
        "box_size": 7,
        "p_infection_per_day": 0.2,
        "initial_infected_ratio": 0.1,
        "initial_recovered_ratio": 0.0,
        "infection_time": 5,
        "travel_rate": 0,
        "limit_social_distancing_to_infectious": False        
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(self.population_ratios)
        print(kwargs)

    def add_people(self):
        people = VGroup()
        for box in self.boxes:
            dl_bound = box.get_corner(DL)
            ur_bound = box.get_corner(UR)
            box.people = VGroup()
            for person_type, ratio in self.population_ratios.items():
                population_size = int(ratio * self.city_population)
                for x in range(population_size):
                    person = person_type(
                        dl_bound=dl_bound,
                        ur_bound=ur_bound
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

class SIRDeconfSim(SIRSimulation):
    
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

    def add_simulation(self):
        self.simulation = MultiPopSIRSimulation(**self.simulation_config)
        self.add(self.simulation)
        
class PartiallyRespectedMeasures(RunSimpleDeconfSimulation):
    CONFIG = {
        "simulation_config": {
        "population_ratios": {
            RespectfulCitizen: 0.5, 
            DisrespectfulCitizen: 0.5}
        }
    }
    
class ToggledConfinement(RunSimpleSimulation):
    CONFIG = {
        "simulation_config": {
            "p_infection_per_day": 0.2
        },
        "activation_treshold": 10}
    
    def construct(self):
        self.confinement = False
        for person in self.simulation.people:
            person.social_distance_factor=0
            
        self.run_until_zero_infections()
    def check_if_confinement(self):
        
        infected_count = self.simulation.get_status_counts()[1]
        
        if not self.confinement:
            if infected_count > self.activation_treshold:
                for person in self.simulation.people:
                    person.social_distance_factor=1
                self.confinement = True
        else:
            if infected_count < self.activation_treshold:
                for person in self.simulation.people:
                    person.social_distance_factor=0
                self.confinement = False
    
    def run_until_zero_infections(self):
        while True:
            self.wait(5)
            self.check_if_confinement()
            if self.simulation.get_status_counts()[1] == 0:
                self.wait(5)
                break

            
    
    
    
    


