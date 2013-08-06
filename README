## tsp-genetic-python
### An genetic algorithm to solve the Travelling Salesman Problem implemented in Python 3

#### Usage
Run with:

	> python tsp-genetic-python.py

All parameters are configure at the top of the tsp-genetic-python.py file. Parameters are documented in the code.

Cities can read from a .csv file. This is specified by the `csv_name` variable, provided that `csv_cities = True`. The .csv file must contain one city per line in the following format:

	name,x,y
	name,x,y
	name,x,y
	...

Alternatively, cities can be specified directly as `City` objects. This is seen in the code around line 730. Provided are some sample cities in a 200 x 200 grid, as well as the Australian capitals (not hard to solve, just go round in a straight line). If I remember correctly, the provided cities.csv file contains the state capitals of the USA. With 48 cities this dataset is quite hard to solve and the algorithm struggles. 

#### GUI
The program has a GUI:  
![Screenshot](https://raw.github.com/frigaardj/tsp-genetic-python/master/screenshot.png "App screenshot")

The 'map' will automatically rescale to encompass all of the cities.
#### Breeding/crossover
Breeding is done by selecting a random range of cities from the first parent route, and placing it into an empty child route (in the same range). Gaps are then filled in, without duplicates, in the order they appear in the second parent route. For example:

    parent1: 0123456789
    parent1: 5487961320

    start_pos = 0 (random)
    end_pos = 4 (random)

    unfilled child: 01234*****
    filled child:   0123458796

    Each number represents a city. Asterisks are unfilled.

This algorithm conserves some of the order of the routes, but is not ideal. In the code, a method called `crossover_experimental()` is implemented but not used. This takes a random city and branches out left from the first parent route and right from the second parent until it hits a limit, then fills the gaps in randomly. It conserves the order of both routes from a central point. I'm still testing it.

#### Mutation
Mutation is done by swapping two random cities:
	
	123456789 --> 123546789

This is primitive but does a reasonable job. The algorithm is most effective with a reasonable high rate of mutation (`0.3+`).

#### Evolution
Population evolution is achieved by filling a new population with new children from pairs of two tournament-winning parents. If `elitism` is set to `True`, the fittest from the initial population will also be carried over.

#### Future
In the future I might implement the [2opt](http://en.wikipedia.org/wiki/2-opt) manœuvre, since the algorithm often seems to get stuck with routes crossing over.