# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './from_3b1b/active/')
from manimlib.imports import *
from sir import Person, SIRSimulation, RunSimpleSimulation, COLOR_MAP

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

class SquarePerson(Person):
    def get_body(self):
        return Square()
"""
class SIRGraphDead(SIRGraph):
    def get_graph(self, data):
        axes = self.axes
        i_points = []
        s_points = []
        c_points = []
        for x, props in zip(np.linspace(0, 1, len(data)), data):
            i_point = axes.c2p(x, props[1])
            s_point = axes.c2p(x, sum(props[:2]))
            c_point = axes.c2p(x, props[2])
            i_points.append(i_point)
            s_points.append(s_point)
            #c_points.append(c_point)

        c_points = [
            axes.c2p(0, 1),
            axes.c2p(1, 1),
            *s_points[::-1],
            axes.c2p(0, 1),
        ]
        s_points.extend([
            *i_points[::-1],
            s_points[0],
        ])
        i_points.extend([
            axes.c2p(1, 0),
            axes.c2p(0, 0),
            i_points[0],
        ])
        points_lists = [s_points, i_points, c_points]
        regions = VGroup(VMobject(), VMobject(), VMobject())

        for region, status, points in zip(regions, "SIC", points_lists):
            region.set_points_as_corners(points)
            region.set_stroke(width=0)
            region.set_fill(self.color_map[status], 1)
        regions[0].set_fill(opacity=0.5)

        return regions

class GraphBracesDead(GraphBraces):
    def __init__(self, graph, simulation, **kwargs):
        super().__init__(**kwargs)
        axes = self.axes = graph.axes
        self.simulation = simulation

        ys = np.linspace(0, 1, 4)
        self.lines = VGroup(*[
            Line(axes.c2p(1, y1), axes.c2p(1, y2))
            for y1, y2 in zip(ys, ys[1:])
        ])
        self.braces = VGroup(*[Brace(line, RIGHT) for line in self.lines])
        self.labels = VGroup(
            TextMobject("Susceptible", color=COLOR_MAP["S"]),
            TextMobject("Infectious", color=COLOR_MAP["I"]),
            TextMobject("Saved", color=COLOR_MAP["C"]),
        )

        self.max_label_height = graph.get_height() * 0.05

        self.add(self.braces, self.labels)
        self.max_label_height = graph.get_height() * 0.05

        self.add(self.braces, self.labels)

        self.time = 0
        self.last_update_time = -1
        self.add_updater(update_time)
        self.add_updater(lambda m: m.update_braces())
        self.update(0)
"""
class MultiPopSIRSimulation(SIRSimulation):
    CONFIG = {
        "n_cities": 1,
        "city_population": 100,
        "box_size": 7,
        "population_ratios": {SquarePerson: 0.2, DotPerson: 0.8},
        "p_infection_per_day": 0.2,
        "infection_time": 5,
        "travel_rate": 0,
        "limit_social_distancing_to_infectious": False
        }

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

        # Choose a patient zero
        random.choice(people).set_status("I")
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
