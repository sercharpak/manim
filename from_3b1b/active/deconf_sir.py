# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './from_3b1b/active/')
from manimlib.imports import *
from sir import Person, SIRSimulation, RunSimpleSimulation, DelayedSocialDistancing, PiPerson

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
class YoungPerson(DotPerson):
    CONFIG = {
        "social_distance_factor": 0.7,
        "goes_to_school_probability": 0.7,
        #"infection_radius": 0.3,
        }
class OldPerson(PiPerson):
    CONFIG = {
        "social_distance_factor": 1.0,
        #"infection_radius": 0.25,
        "goes_to_school_probability": -1.0,
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
            RespectfulCitizen: 0.6,
            DisrespectfulCitizen: 0.4}
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

class YoungAndOldPeople(RunSimpleDeconfSimulation):
    CONFIG = {
        "simulation_config": {
            'city_population': 200,
            "population_ratios": {
                YoungPerson: 0.6,
                OldPerson: 0.4},
        }
    }

class School(YoungAndOldPeople):
    CONFIG = {
        "sd_probability": 0.7,
        "delay_time": 5,
        "school_frequency": 0.05,
        "school_time": 1,
    }

    # SDHC - Right Bottom Quarter
    def findRightBottomQuarterCenter(self,pBox):
        left_box = pBox.get_left()
        right_box = pBox.get_right()
        bottom_box = pBox.get_bottom()
        top_box = pBox.get_top()
        position_to_return = right_box / 2 + bottom_box / 2
        return position_to_return

    def setup(self):
        super().setup()
        for person in self.simulation.people:
            person.last_school_trip = -3
            person.is_in_school = False

        triangle = Triangle()
        triangle.set_height(0.2)
        triangle.set_color(WHITE)
        left_box = self.simulation.boxes[0].get_left()
        right_box = self.simulation.boxes[0].get_right()
        bottom_box = self.simulation.boxes[0].get_bottom()
        top_box = self.simulation.boxes[0].get_top()
        # SDHC - Right Bottom Quarter
        position_school = self.findRightBottomQuarterCenter(self.simulation.boxes[0])
        triangle.move_to(position_school)
        self.position_school=position_school
        self.add(triangle)

        self.simulation.add_updater(
            lambda m, dt: self.add_travel_anims(m, dt)
        )
    def construct(self):
        self.run_until_zero_infections()

    def add_travel_anims(self, simulation, dt):
        school_time = self.school_time
        for person in simulation.people:
            if person.goes_to_school_probability>0:
                time_since_trip = person.time - person.last_school_trip
                if time_since_trip > school_time:
                    # SDHC probably a better way to deal with the fact that they all go
                    if random.random() < person.goes_to_school_probability*self.school_frequency:
                        person.last_school_trip = person.time
                        # SDHC - Right Bottom Quarter
                        where_to_move_point = self.findRightBottomQuarterCenter(person.box)
                        point = VectorizedPoint(person.get_center())
                        anim1 = ApplyMethod(
                            point.move_to, where_to_move_point,
                            path_arc=45 * DEGREES,
                            run_time=school_time,
                            rate_func=there_and_back_with_pause,
                        )
                        anim2 = MaintainPositionRelativeTo(person, point, run_time=school_time)

                        person.push_anim(anim1)
                        person.push_anim(anim2)

    def add_sliders(self):
        pass
    
    
    
    
# MarketClosesAndReopens
class SchoolClosingReOpening(School):
    CONFIG = {
        "simulation_config": {
            "city_population": 200,
            "box_size":7,
        "initial_infected_ratio": 0.01,
        "initial_recovered_ratio": 0.05,
        },

        "sd_probability": 0.9,
        "delay_time": 0.1,
        "p_infection_per_day": 0.05,
        "school_frequency": 0.1,
        "original_frequency":0.00,
        "closing_proportion":0.05,
        "opening_proportion":0.15,
        "is_open":1,
    }
    def close(self):
        """Closes the school, it changes the frequency to 0."""
        school_frequency = 0.0
        self.school_frequency = school_frequency
        self.is_open=0


    def open(self):
        """Opens the school, it changes the frequency back to the original."""
        school_frequency = self.original_frequency
        self.school_frequency = school_frequency
        self.is_open = 1

    def get_infectious_proportion(self):
        """Gets the proportion of infectious people with respect to the total population"""
        all_status_count = np.sum(self.simulation.get_status_counts())
        infected_count = self.simulation.get_status_counts()[1]
        return infected_count/all_status_count

    def get_recovered_proportion(self):
        """Gets the proportion of recovered people with respect to the total population"""
        all_status_count = np.sum(self.simulation.get_status_counts())
        recovered_count = self.simulation.get_status_counts()[2]
        return recovered_count / all_status_count

    def construct(self):
        self.original_frequency = self.school_frequency
        self.run_until_zero_infections()

    def run_until_zero_infections(self):
        while True:
            if (self.is_open) & (self.get_infectious_proportion() > self.closing_proportion):
                self.close()
            if (not self.is_open) & (self.get_recovered_proportion() > self.opening_proportion):
                self.open()
            self.wait(1)
            if self.simulation.get_status_counts()[1] == 0:
                self.wait(1)
                break




