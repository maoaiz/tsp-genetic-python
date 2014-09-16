'''
Genetic Algorithm for the Travelling Salesman Problem
v1.0

by

JackFrigaard
mail@jackf.net

Written for Python 3.1+

'''

import random
import copy
import os
import time
import math
import csv

try:
    from tkinter import *
    from tkinter.ttk import *
except Exception, e:
    print "[ERROR]:", e
    from Tkinter import *

list_of_cities =[]

#########################################
######                             ######
######    Algorithm paremeters:    ######
######                             ######
#########################################

# probability that an individual Route will mutate
k_mut_prob = 0.2

# Number of generations to run for
k_n_generations = 100
# Population size of 1 generation (RoutePop)
k_population_size = 100

# Size of the tournament selection. 
tournament_size = 7

# If elitism is True, the best from one generation will carried over to the next.
elitism = True

# Read city data from csv?
csv_cities = False

# Full path for csv file. The r prefix avoids any conflicts with backslashes.
csv_name = 'cities.csv'


# City class
class City(object):
    """
    Stores City objects. Upon initiation, automatically appends itself to list_of_cities

    self.x: x-coord
    self.y: y-coord
    self.graph_x: x-coord for graphic representation
    self.graph_y: y-coord for graphic representation
    self.name: human readable name.
    self.distance_to: dictionary of distances to other cities (keys are city names, values are floats)

    """
    def __init__(self, name, x, y, distance_to={}):
        # Name and coordinates:
        self.name = name
        self.x = self.graph_x = x
        self.y = self.graph_y = y
        # Appends itself to the global list of cities:
        list_of_cities.append(self)
        # Creates a dictionary of the distances to all the other cities (has to use a value so uses itself - always 0)
        # self.distance_to = {self.name:0.0}
        self.distance_to = distance_to

    def calculate_distances(self): 
        '''
        self --> None

        Calculates the distances of the
        city to all other cities in the global 
        list list_of_cities, and places these values 
        in a dictionary called self.distance_to
        with city name keys and float values
        ''' 
        for city in list_of_cities:
            tmp_dist = self.point_dist(self.x, self.y, city.x, city.y)
            self.distance_to[city.name] = tmp_dist
        # print "ready", self.distance_to

    # Calculates the distance between two cartesian points..
    def point_dist(self, x1,y1,x2,y2):
        return ((x1-x2)**2 + (y1-y2)**2)**(0.5)


# Route Class
class Route(object):
    """
    Stores an ordered list of all the City objects in the global list_of_cities.
    Also stores information about the route.

    self.route: list of cities in list_of_cities. Randomly shuffled upon __init__
    self.length: float length of route (full loop)

    self.is_valid_route(): Returns True if the route contains all cities in list_of_cities ONCE and ONLY ONCE
    self.pr_cits_in_rt(): Prints all the cities in the route, in the form <cityname1,cityname2,cityname3...>
    self.pr_vrb_cits_in_rt: Prints all the coordinate pairs of the cities in the route, in the form <|x,y|x,y|x,y|...>
    """
    def __init__(self):
        # initiates a route attribute equal to a randomly shuffled list_of_cities
        self.route = sorted(list_of_cities, key=lambda *args: random.random())
        ### Calculates its length:
        self.recalc_rt_len()

    def recalc_rt_len(self):
        '''
        self --> None

        Method to re-calculate the route length
        if the self.route attribute has been changed manually.
        '''
        # Zeroes its length
        self.length = 0.0
        # for every city in its route attribute:
        for city in self.route:
            # set up a next city variable that points to the next city in the list 
            # and wraps around at the end:
            next_city = self.route[self.route.index(city)-len(self.route)+1]
            # Uses the first city's distance_to attribute to find the distance to the next city:
            dist_to_next = city.distance_to[next_city.name]
            # adds this length to its length attr.
            self.length += dist_to_next

    def pr_cits_in_rt(self, print_route=False):
        '''
        self --> None

        Prints all the cities in the route, in the form <cityname1,cityname2,cityname3...>
        '''
        cities_str = ''
        for city in self.route:
            cities_str += city.name + ','
        cities_str = cities_str[:-1] # chops off last comma
        if print_route:
            print('    ' + cities_str)

    def pr_vrb_cits_in_rt(self):
        '''
        self --> None

        Prints all the coordinate pairs of the cities in the route, in the form <|x,y|x,y|x,y|...>
        '''
        cities_str = '|'
        for city in self.route:
            cities_str += str(city.x) + ',' + str(city.y) + '|'
        print(cities_str)

    def is_valid_route(self):
        '''
        self --> Bool()

        Returns True if the route contains all cities in list_of_cities ONCE and ONLY ONCE
        i.e. returns False if there are duplicates.

        Use: if there are multiples of the same city in a route,
        it will converge until all the cities are that same city (length = 0)
        '''
        for city in list_of_cities:
            # helper function defined up to
            if self.count_mult(self.route,lambda c: c.name == city.name) > 1:
                return False
        return True

    # Returns the number of pred in sequence (duplicate checking.)
    def count_mult(self, seq, pred):
        return sum(1 for v in seq if pred(v))


# Contains a population of Route() objects
class RoutePop(object):
    """
    Contains a list of route objects and provides info on them.

    self.rt_pop: list of Route objects
    self.size: lenth of rt_pop - specified upon __init__
    self.fittest: Route() object with shortest length from self.rt_pop

    self.get_fittest(): Calcualtes fittest route, sets self.fittest to it, and returns the Route. Use if routes have changed manually.
    """
    def __init__(self, size, initialise):
        self.rt_pop = []
        self.size = size
        # If we want to initialise a population.rt_pop:
        if initialise:
            for x in range(0,size):
                new_rt = Route()
                self.rt_pop.append(new_rt)
            self.get_fittest()

    def get_fittest(self):
        '''
        self --> Route()

        Returns the two shortest routes in the population, in a list called self.top_two
        '''
        # sorts the list based on the routes' lengths
        sorted_list = sorted(self.rt_pop, key=lambda x: x.length, reverse=False)
        self.fittest = sorted_list[0]
        return self.fittest


# Class for bringing together all of the methods to do with the Genetic Algorithm
class GA(object):
    """
    Class for running the genetic algorithm. Do not __init__ - Class only provides methods. 

    crossover(parent1, parent2): Returns a child route after breeding the two parent routes. 

    """
    def crossover_experimental(routeA,routeB):
        '''
            Experimental crossover algorithm using a spidering-out idea. Less effective at the moment.
        '''
        # new child Route()
        child_rt = Route()


        # prevents from recalculating
        routeB_len = len(routeB.route)

        # Chooses a random city
        random_city = random.choice(list_of_cities)

        # routeA going down
        # routeB going up

        incrementing_a = True
        incrementing_b = True

        idx_a = routeA.route.index(random_city)
        idx_b = routeB.route.index(random_city)

        idx_a -= 1
        idx_b += 1

        if idx_a < 0:
            incrementing_a = False

        if idx_b >= routeB_len:
            incrementing_b = False

        child_rt.route = [random_city]

        # print(random_city.name)

        while (incrementing_a and incrementing_b):
            # print('idx_a: {}'.format(idx_a))

            if idx_a >= 0:
                if not (routeA.route[idx_a] in child_rt.route):
                    child_rt.route.insert(0, routeA.route[idx_a])

            idx_a -= 1

            if idx_a < 0:
                incrementing_a = False
                break

            # child_rt.pr_cits_in_rt()


            if idx_b < routeB_len:
                if not (routeB.route[idx_b] in child_rt.route):
                    child_rt.route.append(routeB.route[idx_b])

            idx_b += 1

            if idx_b >= routeB_len:
                incrementing_b = False
                break

            # print('idx_b: {}'.format(idx_b))
            # child_rt.pr_cits_in_rt()

        # now either incrementing_a or incementing_b must be false

        shuffled_cities = sorted(routeA.route, key=lambda *args: random.random())
        for city in shuffled_cities:
            if not city in child_rt.route:
                child_rt.route.append(city)

        return child_rt

    def crossover(self, parent1, parent2):
        '''
        Route(), Route() --> Route()

        Returns a child route Route() after breeding the two parent routes. 
        Routes must be of same length.

        Breeding is done by selecting a random range of parent1, and placing it into the empty child route (in the same place).
        Gaps are then filled in, without duplicates, in the order they appear in parent2.

        For example:
            parent1: 0123456789
            parent1: 5487961320

            start_pos = 0
            end_pos = 4

            unfilled child: 01234*****
            filled child:   0123458796

            * = None

        '''



        # new child Route()
        child_rt = Route()

        for x in range(0,len(child_rt.route)):
            child_rt.route[x] = None

        # Two random integer indices of the parent1:
        start_pos = random.randint(0,len(parent1.route))
        end_pos = random.randint(0,len(parent1.route))


        #### takes the sub-route from parent one and sticks it in itself:
        # if the start position is before the end:
        if start_pos < end_pos:
            # do it in the start-->end order
            for x in range(start_pos,end_pos):
                child_rt.route[x] = parent1.route[x] # set the values to eachother
        # if the start position is after the end:
        elif start_pos > end_pos:
            # do it in the end-->start order
            for i in range(end_pos,start_pos):
                child_rt.route[i] = parent1.route[i] # set the values to eachother


        # Cycles through the parent2. And fills in the child_rt
        # cycles through length of parent2:
        for i in range(len(parent2.route)):
            # if parent2 has a city that the child doesn't have yet:
            if not parent2.route[i] in child_rt.route:
                # it puts it in the first 'None' spot and breaks out of the loop.
                for x in range(len(child_rt.route)):
                    if child_rt.route[x] == None:
                        child_rt.route[x] = parent2.route[i]
                        break
        # repeated until all the cities are in the child route

        # returns the child route (of type Route())
        child_rt.recalc_rt_len()
        return child_rt

    def mutate(self, route_to_mut):
        '''
        Route() --> Route()

        Swaps two random indexes in route_to_mut.route. Runs k_mut_prob*100 % of the time
        '''
        # k_mut_prob %
        if random.random() < k_mut_prob:

            # two random indices:
            mut_pos1 = random.randint(0,len(route_to_mut.route)-1)
            mut_pos2 = random.randint(0,len(route_to_mut.route)-1)

            # if they're the same, skip to the chase
            if mut_pos1 == mut_pos2:
                return route_to_mut

            # Otherwise swap them:
            city1 = route_to_mut.route[mut_pos1]
            city2 = route_to_mut.route[mut_pos2]

            route_to_mut.route[mut_pos2] = city1
            route_to_mut.route[mut_pos1] = city2

        # Recalculate the length of the route (updates it's .length)
        route_to_mut.recalc_rt_len()

        return route_to_mut

    def mutate_2opt(route_to_mut):
        '''
        Route() --> Route()

        Swaps two random indexes in route_to_mut.route. Runs k_mut_prob*100 % of the time
        '''
        # k_mut_prob %
        if random.random() < k_mut_prob:

            for i in range(len(route_to_mut.route)):
                for ii in range(len(route_to_mut.route)): # i is a, i + 1 is b, ii is c, ii+1 is d
                    if (route_to_mut.route[i].distance_to[route_to_mut.route[i-len(route_to_mut.route)+1].name]
                     + route_to_mut.route[ii].distance_to[route_to_mut.route[ii-len(route_to_mut.route)+1].name]
                     > route_to_mut.route[i].distance_to[route_to_mut.route[ii].name]
                     + route_to_mut.route[i-len(route_to_mut.route)+1].distance_to[route_to_mut.route[ii-len(route_to_mut.route)+1].name]):

                        c_to_swap = route_to_mut.route[ii]
                        b_to_swap = route_to_mut.route[i-len(route_to_mut.route)+1]

                        route_to_mut.route[i-len(route_to_mut.route)+1] = c_to_swap
                        route_to_mut.route[ii] = b_to_swap 

            route_to_mut.recalc_rt_len()

        return route_to_mut

    def tournament_select(self, population):
        '''
        RoutePop() --> Route()

        Randomly selects tournament_size amount of Routes() from the input population.
        Takes the fittest from the smaller number of Routes(). 

        Principle: gives worse Routes() a chance of succeeding, but favours good Routes()
        '''

        # New smaller population (not intialised)
        tournament_pop = RoutePop(size=tournament_size,initialise=False)

        # fills it with random individuals (can choose same twice)
        for i in range(tournament_size-1):
            tournament_pop.rt_pop.append(random.choice(population.rt_pop))
        
        # returns the fittest:
        return tournament_pop.get_fittest()

    def evolve_population(self, init_pop):
        '''
        RoutePop() --> RoutePop()

        Takes a population and evolves it then returns the new population. 
        '''

        #makes a new population:
        descendant_pop = RoutePop(size=init_pop.size, initialise=True)

        # Elitism offset (amount of Routes() carried over to new population)
        elitismOffset = 0

        # if we have elitism, set the first of the new population to the fittest of the old
        if elitism:
            descendant_pop.rt_pop[0] = init_pop.fittest
            elitismOffset = 1

        # Goes through the new population and fills it with the child of two tournament winners from the previous populatio
        for x in range(elitismOffset,descendant_pop.size):
            # two parents:
            tournament_parent1 = self.tournament_select(init_pop)
            tournament_parent2 = self.tournament_select(init_pop)

            # A child:
            tournament_child = self.crossover(tournament_parent1, tournament_parent2)

            # Fill the population up with children
            descendant_pop.rt_pop[x] = tournament_child

        # Mutates all the routes (mutation with happen with a prob p = k_mut_prob)
        for route in descendant_pop.rt_pop:
            if random.random() < 0.3:
                self.mutate(route)

        # Update the fittest route:
        descendant_pop.get_fittest()

        return descendant_pop






class App(object):
    """
    Runs the application
    """
    def __init__(self,n_generations,pop_size, graph=False):
        '''
        Initiates an App object to run for n_generations with a population of size pop_size
        '''

        if csv_cities:
            self.read_csv()

        self.n_generations = n_generations
        self.pop_size = pop_size

        # Once all the cities are defined, calcualtes the distances for all of them.
        # for city in list_of_cities:
        #     city.calculate_distances()
        if graph:
            self.set_city_gcoords()
            
            # Initiates a window object & sets its title
            self.window = Tk()
            self.window.wm_title("Generation 0")

            # initiates two canvases, one for current and one for best
            self.canvas_current = Canvas(self.window, height=300, width=300)
            self.canvas_best = Canvas(self.window, height=300, width=300)

            # Initiates two labels
            self.canvas_current_title = Label(self.window, text="Best route of current gen:")
            self.canvas_best_title = Label(self.window, text="Overall best so far:")

            # Initiates a status bar with a string
            self.stat_tk_txt = StringVar()
            self.status_label = Label(self.window, textvariable=self.stat_tk_txt, relief=SUNKEN, anchor=W)

            # creates dots for the cities on both of the canvases
            for city in list_of_cities:
                self.canvas_current.create_oval(city.graph_x-2, city.graph_y-2, city.graph_x + 2, city.graph_y + 2, fill='blue')
                self.canvas_best.create_oval(city.graph_x-2, city.graph_y-2, city.graph_x + 2, city.graph_y + 2, fill='blue')

            # Packs all the widgets (physically creates them and places them in order)
            self.canvas_current_title.pack()
            self.canvas_current.pack()
            self.canvas_best_title.pack()
            self.canvas_best.pack()
            self.status_label.pack(side=BOTTOM, fill=X)

            # Runs the main window loop
            self.window_loop()
        else:
            print "Calculating GA_loop"
            self.GA_loop(n_generations,pop_size, graph=graph)

    def set_city_gcoords(self):
        '''
        All cities have graph_x and graph_y attributes that are only referenced when showing them on the map.
        This method takes the original city.x and city.y and transforms them so that the coordinates map fully onto the 300x300 map view.
        '''

        # defines some variables (we will set them next)
        min_x = 100000
        max_x = -100000
        min_y = 100000
        max_y = -100000

        #finds the proper maximum/minimum
        for city in list_of_cities:

            if city.x < min_x:
                min_x = city.x
            if city.x > max_x:
                max_x = city.x

            if city.y < min_y:
                min_y = city.y
            if city.y > max_y:
                max_y = city.y

        # shifts the graph_x so the leftmost city starts at x=0, same for y.
        for city in list_of_cities:
            city.graph_x = (city.graph_x + (-1*min_x))
            city.graph_y = (city.graph_y + (-1*min_y))

        # resets the variables now we've made changes
        min_x = 100000
        max_x = -100000
        min_y = 100000
        max_y = -100000

        #finds the proper maximum/minimum
        for city in list_of_cities:

            if city.graph_x < min_x:
                min_x = city.graph_x
            if city.graph_x > max_x:
                max_x = city.graph_x

            if city.graph_y < min_y:
                min_y = city.graph_y
            if city.graph_y > max_y:
                max_y = city.graph_y

        # if x is the longer dimension, set the stretch factor to 300 (px) / max_x. Else do it for y. This conserves aspect ratio.
        if max_x > max_y:
            stretch = 300 / max_x
        else:
            stretch = 300 / max_y

        # stretch all the cities so that the city with the highest coordinates has both x and y < 300
        for city in list_of_cities:
            city.graph_x *= stretch
            city.graph_y = 300 - (city.graph_y * stretch)


    def update_canvas(self,the_canvas,the_route,color):
        '''
        Convenience method to update the canvases with the new routes
        '''

        # deletes all current items with tag 'path'
        the_canvas.delete('path')

        # loops through the route
        for i in range(len(the_route.route)):

            # similar to i+1 but will loop around at the end
            next_i = i-len(the_route.route)+1

            # creates the line from city to city
            the_canvas.create_line(the_route.route[i].graph_x,
                                the_route.route[i].graph_y,
                                the_route.route[next_i].graph_x,
                                the_route.route[next_i].graph_y,
                                tags=("path"),
                                fill=color)

            # Packs and updates the canvas
            the_canvas.pack()
            the_canvas.update_idletasks()

    def read_csv(self):
        with open(csv_name, 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                new_city = City(row[0],float(row[1]),float(row[2]))

    def GA_loop(self,n_generations,pop_size, graph=False):
        '''
        Main logic loop for the GA. Creates and manages populations, running variables etc.
        '''

        # takes the time to measure the elapsed time
        start_time = time.time()

        # Creates the population:
        print "Creates the population:"
        the_population = RoutePop(pop_size, True)
        print "Finished Creates the population"

        # the_population.rt_pop[0].route = [1,8,38,31,44,18,7,28,6,37,19,27,17,43,30,36,46,33,20,47,21,32,39,48,5,42,24,10,45,35,4,26,2,29,34,41,16,22,3,23,14,25,13,11,12,15,40,9]
        # the_population.rt_pop[0].recalc_rt_len()
        # the_population.get_fittest()

        #checks to make sure there are no duplicate cities:
        if the_population.fittest.is_valid_route() == False:
            raise NameError('Multiple cities with same name. Check cities.')
            return # if there are, raise a NameError and return

        # gets the best length from the first population (no practical use, just out of interest to see improvements)
        initial_length = the_population.fittest.length

        # Creates a random route called best_route. It will store our overall best route.
        best_route = Route()

        if graph:
            # Update the two canvases with the just-created routes:
            self.update_canvas(self.canvas_current,the_population.fittest,'red')
            self.update_canvas(self.canvas_best,best_route,'green')


        # Main process loop (for number of generations)
        for x in range(1,n_generations):
            # Updates the current canvas every n generations (to avoid it lagging out, increase n)
            if x % 8 == 0 and graph:
                self.update_canvas(self.canvas_current,the_population.fittest,'red')

            # Evolves the population:
            the_population = GA().evolve_population(the_population)

            # If we have found a new shorter route, save it to best_route
            if the_population.fittest.length < best_route.length:
                # set the route (copy.deepcopy because the_population.fittest is persistent in this loop so will cause reference bugs)
                best_route = copy.deepcopy(the_population.fittest)
                if graph:
                    # Update the second canvas because we have a new best route:
                    self.update_canvas(self.canvas_best,best_route,'green')
                    # update the status bar (bottom bar)
                    self.stat_tk_txt.set('Initial length {0:.2f} Best length = {1:.2f}'.format(initial_length,best_route.length))
                    self.status_label.pack()
                    self.status_label.update_idletasks()

            # Prints info to the terminal:
            self.clear_term()
            print('Generation {0} of {1}'.format(x,n_generations))
            print(' ')
            print('Overall fittest has length {0:.2f}'.format(best_route.length))
            print('and goes via:')
            best_route.pr_cits_in_rt()
            print(' ')
            print('Current fittest has length {0:.2f}'.format(the_population.fittest.length))
            print('And goes via:')
            the_population.fittest.pr_cits_in_rt()
            print(' ')
            print('''The screen with the maps may become unresponsive if the population size is too large. It will refresh at the end.''')

            if graph:
                # sets the window title to the latest Generation:
                self.window.wm_title("Generation {0}".format(x))
        if graph:
            # sets the window title to the last generation
            self.window.wm_title("Generation {0}".format(n_generations))

            # updates the best route canvas for the last time:
            self.update_canvas(self.canvas_best,best_route,'green')
            
        # takes the end time of the run:
        end_time = time.time()

        # Prints final output to terminal:
        self.clear_term()
        print('Finished evolving {0} generations.'.format(n_generations))
        print("Elapsed time was {0:.1f} seconds.".format(end_time - start_time))
        print(' ')
        print('Initial best distance: {0:.2f}'.format(initial_length))
        print('Final best distance:   {0:.2f}'.format(best_route.length))
        print('The best route went via:')
        best_route.pr_cits_in_rt(print_route=True)

    def window_loop(self):
        '''
        Wraps the GA_loop() method and initiates the window on top of the logic.
        window.mainloop() hogs the Thread, that's why the GA_loop is called as a callback
        '''
        # see http://stackoverflow.com/questions/459083/how-do-you-run-your-own-code-alongside-tkinters-event-loop
        self.window.after(0,self.GA_loop(self.n_generations, self.pop_size))
        self.window.mainloop()

    # Helper function for clearing terminal window
    def clear_term(self):
        os.system('cls' if os.name=='nt' else 'clear')

##############################
#### Declare cities here: ####
##############################

# Australian Cities:
# adelaide = City('adelaide', 138.60, -34.93)
# brisbane = City('brisbane', 153.02, -27.47)
# canberra = City('canberra', 149.13, -35.30)
# darwin = City('darwin', 130.83, -12.45)
# hobart = City('hobart', 147.32, -42.88)
# melbourne = City('melbourne', 144.97, -37.82)
# perth = City('perth', 115.85, -31.95)
# sydney = City('sydney', 151.20, -33.87)

## Random cities
# i = City('c1', 10, 2)
# j = City('c2', 1, 22)
# k = City('c3', 2, 13)


def specific_cities():
    """function to calculate the route for files in data folder"""
    try:
        start_time = time.time()
        # f = open("data/3x3.in", "r")
        f = open("data/bays29.in", "r")
        # f = open("data/d493.in", "r")
        # f = open("data/pr2392.in", "r")
        lines = int(f.readline())
        for i, li in enumerate(f.readlines(), start=1):
            os.system('cls' if os.name=='nt' else 'clear')
            print "Leyendo '{}': {}/{} lineas".format(f.name, i, lines)
            d = {}
            for j, line in enumerate(map(float, li.split()), start=1):
                d["C" + str(j)] = line
            tmp = City("C" + str(i), 10, 10, d)
            i += 1
        print("--- %s seconds ---" % str(time.time() - start_time))
        band = True
    except Exception, e:
        print e
        band = False
    if band:
        print "Buscando la ruta mas corta para el viajero..."
        try:
            start_time = time.time()
            app = App(n_generations=k_n_generations,pop_size=k_population_size)
            print("---Ruta encontrada en %s seconds ---" % str(time.time() - start_time))
        except Exception, e:
            print "\n[ERROR]: %s\n" % e


def random_cities():
    i = City('i', 60, 200)
    j = City('j', 180, 190)
    k = City('k', 100, 180)
    l = City('l', 140, 180)
    m = City('m', 20, 160)
    n = City('n', 100, 160)
    o = City('o', 140, 140)
    p = City('p', 40, 120)
    q = City('q', 100, 120)
    r = City('r', 180, 100)
    s = City('s', 60, 80)
    t = City('t', 120, 80)
    u = City('u', 180, 60)
    v = City('v', 20, 40)
    w = City('w', 100, 40)
    x = City('x', 200, 40)
    a = City('a', 20, 20)
    b = City('b', 60, 20)
    c = City('c', 160, 20)
    d = City('d', 68, 130)
    e = City('e', 10, 10)
    f = City('f', 75, 180)
    g = City('g', 190, 190)
    h = City('h', 200, 10)
    # a1 = City('a1', 53, 99)

    for city in list_of_cities:
        city.calculate_distances()
    ######## create and run an application instance:
    app = App(n_generations=k_n_generations,pop_size=k_population_size, graph=True)

if __name__ == '__main__':
    """Select only one function: random or specific"""
    specific_cities()
    # random_cities()

