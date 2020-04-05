# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './from_3b1b/active/')
from manimlib.imports import *
from sir import Person, SIRSimulation, RunSimpleSimulation, COLOR_MAP, DelayedSocialDistancing, PiPerson

# Change of the color map to take into account the new categories
COLOR_MAP["D"] = PURPLE # a dead person
COLOR_MAP["C"] = WHITE # a clean person
COLOR_MAP["H"] = GREEN # a hospitalized person

class PersonGeneralized(Person):
    def set_status(self, status, run_time=1):
        start_color = self.color_map[self.status]
        end_color = self.color_map[status]

        if status == "I":
            self.infection_start_time = self.time
            self.infection_ring.set_stroke(width=0, opacity=0)
            if random.random() < self.p_symptomatic_on_infection:
                self.symptomatic = True
            else:
                self.infection_ring.set_color(self.asymptomatic_color)
                end_color = self.asymptomatic_color
        if self.status == "I":
            self.infection_end_time = self.time
            self.symptomatic = False

        anims = [
            UpdateFromAlphaFunc(
                self.body,
                lambda m, a: m.set_color(interpolate_color(
                    start_color, end_color, a
                )),
                run_time=run_time,
            )
        ]
        for anim in anims:
            self.push_anim(anim)

        self.status = status


class DotPerson(Person):
    def get_body(self):
        return Dot()
    
class SmallDotPerson(Person):
    def get_body(self):
        return SmallDot()
    
class SquarePerson(Person):
    def get_body(self):
        return Square()

class SmallSquarePerson(Person):
    def get_body(self):
        return SmallSquare()

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
class YoungPerson(SmallDotPerson):
    CONFIG = {
        "social_distance_factor": 0.8,
        "goes_to_school_probability": 0.7,
        #"infection_radius": 0.3,
        }
class OldPerson(SmallSquarePerson):
    CONFIG = {
        "social_distance_factor": 0.9,
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

class SIRSimulationH(SIRSimulation):
    CONFIG={
        "person_type": SquarePerson,
        "n_cities": 2,
        "city_population": 100,
        "max_hospital": 5, # max number of people in the hospital
        "proba_dead_hospital": 0.1, # You have a chance of not dying
        "proba_dead_hospital_full": 0.7 # The hospital is full
    }

    def add_boxes(self):
        boxes = VGroup()
        self.n_cities = 2
        for x in range(self.n_cities):
            box = Square()
            box.set_height(self.box_size)
            box.set_stroke(WHITE, 3)
            boxes.add(box)
            self.box_size = 2
        boxes.arrange_in_grid(buff=LARGE_BUFF)
        self.add(boxes)
        self.boxes = boxes

    def get_status_counts(self):
        list_temp = np.array([
            len(list(filter(
                lambda m: m.status == status,
                self.people
            )))
            for status in "SIHCD"
        ])
        return np.array([list_temp[0], list_temp[1] + list_temp[2], list_temp[3] + list_temp[4]])

    def add_people(self):
        people = VGroup()
        for id_box, box in enumerate(self.boxes):
            dl_bound = box.get_corner(DL)
            ur_bound = box.get_corner(UR)
            box.people = VGroup()
            if id_box > 0:
                continue
            self.city_population = 100
            for x in range(self.city_population):
                self.person_type = SquarePerson
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
        list_status = ["S"]
        for individual in people:
            individual.set_status(random.choice(list_status))
        people[0].set_status("I")
        # Choose a patient zero
        #random.choice(people).set_status("I")
        self.add(people)
        self.people = people
    def update_statusses(self, dt):
        for id_box, box in enumerate(self.boxes):
            s_group, i_group, h_group, r_group, d_group = [
                list(filter(
                    lambda m: m.status == status,
                    box.people
                ))
                for status in ["S", "I", "H", "C", "D"]
            ]
            self.total_hospital = len(h_group)
            self.total_dead = len(d_group)

            for s_person in s_group:
                for i_person in i_group:
                    dist = get_norm(i_person.get_center() - s_person.get_center())
                    if dist < s_person.infection_radius and random.random() < self.p_infection_per_day * dt:
                        s_person.set_status("I")
                        i_person.num_infected += 1
            for r_person in r_group:
                if id_box == 1:
                    path_func = path_along_arc(45 * DEGREES)
                    new_box = self.boxes[0]
                    r_person.box.people.remove(r_person)
                    new_box.people.add(r_person)
                    r_person.box = new_box
                    r_person.dl_bound = new_box.get_corner(DL)
                    r_person.ur_bound = new_box.get_corner(UR)

                    r_person.old_center = r_person.get_center()
                    r_person.new_center = new_box.get_center()
                    anim = UpdateFromAlphaFunc(
                        r_person,
                        lambda m, a: m.move_to(path_func(
                            m.old_center, m.new_center, a,
                        )),
                        run_time=1,
                    )
                    r_person.push_anim(anim)
            for i_person in i_group:
                if (i_person.time - i_person.infection_start_time) > self.infection_time:
                    # The person is either in hospital or cured (luck to be change)
                    i_person.set_status(random.choice(["C", "H"]))
            for h_person in h_group:
                if (h_person.time - h_person.infection_start_time) > 1.5*self.infection_time and len(h_group) < self.max_hospital: # to change
                    h_person.set_status(np.random.choice(["C", "D"], size=1, replace=True, p=[1-self.proba_dead_hospital, self.proba_dead_hospital])[0])
                elif (h_person.time - h_person.infection_start_time) > 1.5*self.infection_time and len(h_group) >= self.max_hospital:
                    h_person.set_status(np.random.choice(["C", "D"], 1, True, [1-self.proba_dead_hospital_full, self.proba_dead_hospital_full])[0])
                if id_box > 0:
                    continue
                path_func = path_along_arc(45 * DEGREES)
                new_box = self.boxes[1]
                h_person.box.people.remove(h_person)
                new_box.people.add(h_person)
                h_person.box = new_box
                h_person.dl_bound = new_box.get_corner(DL)
                h_person.ur_bound = new_box.get_corner(UR)

                h_person.old_center = h_person.get_center()
                h_person.new_center = new_box.get_center()
                anim = UpdateFromAlphaFunc(
                    h_person,
                    lambda m, a: m.move_to(path_func(
                        m.old_center, m.new_center, a,
                    )),
                    run_time=1,
                )
                h_person.push_anim(anim)


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
        
        start_dates = np.arange(-self.infection_time, 1)
        

        for person in infected:
            person.set_status("I")
            person.infection_start_time = np.random.choice(start_dates)
        for person in recovered:
            person.set_status("R")
        self.add(people)
        self.people = people

class StartFromDeconf(RunSimpleSimulation):
    def add_simulation(self):
        self.simulation = SIRDeconfSim(**self.simulation_config)
        self.add(self.simulation)

class RunSimpleDeconfSimulation(RunSimpleSimulation):
    def add_simulation(self):
        self.simulation = MultiPopSIRSimulation(**self.simulation_config)
        self.add(self.simulation)

class PartiallyRespectedMeasures(RunSimpleDeconfSimulation):
    CONFIG = {
        "simulation_config": {
        "n_cities": 9,
        "population_ratios": {

            RespectfulCitizen: 0.6,
            DisrespectfulCitizen: 0.4}
        }
    }

class ToggledConfinement(RunSimpleSimulation):
    CONFIG = {
        "simulation_config": {
            "n_cities" : 1,
            "city_population": 250,
            "person_type": SmallDotPerson,
            "person_config": {
                "infection_radius": 0.4
            },
            "p_infection_per_day": 0.3,
            "activation_threshold": 50,
            "release_threshold": 15,
            "post_confinement_sdf": 0.0
        }
    }
    
    def construct(self):
        self.release_confinement()
        self.run_until_zero_infections()
    def policy_change(self):
        infected_count = self.simulation.get_status_counts()[1]
        if not self.confinement:
            return infected_count == 0 or infected_count > self.simulation.activation_threshold
        else:
            return infected_count < self.simulation.release_threshold
    
    def activate_confinement(self):
        for person in self.simulation.people:
            person.social_distance_factor=1
            
        self.simulation.travel_rate=0.0
        
        self.confinement=True
    def release_confinement(self):
        for person in self.simulation.people:
            person.social_distance_factor=self.simulation.post_confinement_sdf
        self.confinement=False
        
    def run_until_zero_infections(self):           
        while True:
            self.wait_until(self.policy_change)
            if self.confinement:
                self.release_confinement()
            else:
                if self.simulation.get_status_counts()[1] == 0:
                    self.wait(5)
                    break
                else:
                    self.activate_confinement()

            
    
    
class EarlyRelease(ToggledConfinement):
    CONFIG = {
        "simulation_config":
            {
                "release_threshold":50
            }
    }

class NormalRelease(ToggledConfinement):
    CONFIG = {
        "simulation_config":
            {
                "release_threshold":30
            }
    }
        
class LateRelease(ToggledConfinement):
    CONFIG = {
        "simulation_config":
            {
                "release_threshold":5
            }
    }
        
class NormalReleasePartialDeconfinement(NormalRelease):
    CONFIG = {
        "simulation_config":
            {
                "post_confinement_sdf": 0.5
            }
        }
    
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
        "sd_probability": 0.9,
        "delay_time": 5,
        "school_frequency": 0.05,
        "school_time": 1,
        "is_open": 0,
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
        if(self.is_open):
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
            "city_population": 250,
            "box_size":7,
        "initial_infected_ratio": 0.02,
        "initial_recovered_ratio": 0.05,
        },

        "sd_probability": 0.65,
        "delay_time": 0.5,
        "p_infection_per_day": 0.2,
        "school_frequency": 0.05,
        "original_frequency":0.00,
        "closing_proportion":0.1, #any above proportion should get the school closed.
        "opening_recovered_proportion":0.15, #Above proportion already recoveres should get the school opened
        "opening_infected_proportion": 0.15, #Except if the infected proportion is above this threshold
        "is_open":0,
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
            has_made_a_modif=0
            if (self.is_open) & (self.get_infectious_proportion() > self.closing_proportion):
                self.close()
                has_made_a_modif=1
            if (not has_made_a_modif) & (not self.is_open) & (self.get_recovered_proportion() > self.opening_recovered_proportion) & (self.get_infectious_proportion()<self.opening_infected_proportion):
                self.open()
            self.wait(5)
            if self.simulation.get_status_counts()[1] == 0:
                self.wait(1)
                break


class RunSimpleHospitalSimulation(RunSimpleSimulation):
    def setup(self):
        self.add_simulation()
        self.position_camera()
        self.add_graph()
        self.add_sliders()
        #self.add_R_label()
        self.add_total_cases_label()
        self.add_total_hospital_label()
        self.add_total_dead_label()

    def add_simulation(self):
        self.simulation = SIRSimulationH(**self.simulation_config)
        self.add(self.simulation)

    def run_until_zero_infections(self):
        while True:
            self.wait(5)
            if self.simulation.get_status_counts()[1] == 0:
                self.wait(5)
                break
        total_dead = 0
        for id_box, box in enumerate(self.simulation.boxes):
            for person in box.people:
                if person.status == "D":
                    total_dead += 1
        print(total_dead)

    def add_total_hospital_label(self):
        label = VGroup(
            TextMobject("\\# Hospital cases = "),
            Integer(1),
            TextMobject("/"),
            TextMobject(str(self.simulation.max_hospital))
        )
        label.arrange(RIGHT)
        label[1].align_to(label[0][0][1], DOWN)
        label.set_color(GREEN)
        boxes = self.simulation.boxes
        label.set_width(0.5 * boxes.get_width())
        label.next_to(boxes, DOWN, buff=0.03 * boxes.get_width())

        label.add_updater(
            lambda m: m[1].set_value(self.simulation.total_hospital)
        )
        self.total_cases_label = label
        self.add(label)
    def add_total_dead_label(self):
        label = VGroup(
            TextMobject("\\# Dead cases = "),
            Integer(1)
        )
        label.arrange(RIGHT)
        label[1].align_to(label[0][0][1], DOWN)
        label.set_color(PURPLE)
        boxes = self.simulation.boxes
        label.set_width(0.5 * boxes.get_width())
        label.next_to(boxes, DOWN + LEFT, buff=0.03 * boxes.get_width())

        label.add_updater(
            lambda m: m[1].set_value(self.simulation.total_dead)
        )
        self.total_cases_label = label
        self.add(label)
