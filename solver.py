from parse import read_input_file, write_output_file, write_input_file, read_output_file
import os
import random
import collections
from Task import *


class population:
    """
    Population of individuals. Contains methods for crossover, and running a population.
    """
    outputloc = None
    def __init__(self, input_loc, size_of_population, num_generations):
        """
        Args:
            input_loc: location of input file.
            size_of_population: number of individuals we would like to evolve in this population.
            num_generations: The number of generations that we would like to run our evolution on.
        Changes:
            population.ouputloc, where this population will dump its best individual for grading.
        """
        self.tasks = read_input_file(input_loc)
        population.outputloc = input_loc.split(".")[0] + "_solution.out"
        self.list_of_individuals = self.get_individuals(size_of_population)
        self.num_generations = num_generations
        self.best_individual = None

    def get_individuals(self, number_of_individuals):
        """
        Creates a list of random individuals to start our population.
        Args:
            number_of_individuals: number of individuals that will be in this population.

        Returns:
            A list of individuals, with randomized tasks in their chromosome.
        """
        return [individual(random.sample(self.tasks, random.randint(0, len(self.tasks)))) for _ in
                range(number_of_individuals)]

    def pull_parents_from_quartile_range(self, population_fitness_list, range):
        range = 1 - range
        index_to_start = round(range * len(list(population_fitness_list.keys())))
        individual = list(population_fitness_list.keys())[random.randint(index_to_start, len(list(population_fitness_list.keys()))) - 1]
        return population_fitness_list[individual]

    def get_suitable_parents(self):
        """
        Takes the individual list for this population, then gets three potential pairings of individuals for mating.
        We mate the best individual that we have found so far with one from the 25% range in our population, 50% range in our population,
        and 75% in our population. TODO: MASSIVE IMPROVEMENTS CAN BE MADE HERE, THIS IS WHERE RESEARCH PAPERS COME IN
        Returns:
            Nested List, with following structure:
                [
                    [best_individual, individual from 25%],
                    [best_individual, individual from 50%],
                    [best_individual, individual from 75%]
                ]
        """
        best_fitness = {}
        for individual in self.list_of_individuals:
            best_fitness[individual.fitness] = individual
        od = collections.OrderedDict(sorted(best_fitness.items()))
        best_individual_one = od[list(od.keys())[-1]]
        individual_from_bottom = self.pull_parents_from_quartile_range(od, .25)
        individual_from_middle = self.pull_parents_from_quartile_range(od, .50)
        individual_from_top = self.pull_parents_from_quartile_range(od, .75)
        return [[best_individual_one, individual_from_bottom], [best_individual_one, individual_from_middle], [best_individual_one, individual_from_top]]

    def return_best_individual(self):
        """
        Gets the best individual in our current population.
        Returns:
            Individual -- with highest fitness.
        """
        best_fitness = {}
        for individual in self.list_of_individuals:
            best_fitness[individual.fitness] = individual
        od = collections.OrderedDict(sorted(best_fitness.items()))
        best_individual = od[list(od.keys())[-1]]
        return best_individual

    def crossover(self, individualone, individualtwo):
        """
        Crossover the chromosomes for our two parents.
        Args:
            individualone: usually the best individual in population.
            individualtwo: Another individual, selected from population.

        Returns:
            An individual --> built from the chromosome of each parent.
            Also adds individual to the current population.
        """
        # Set the crossover point to a uniform random variable in range 1 to the minimum of individual one's chromosome length and individual two's chromosome length
        crossover_point = random.randint(2, min(len(individualone.chromosome), len(individualtwo.chromosome)))
        # Split each chromosome around the crossover point
        gamete_one = individualone.chromosome[:crossover_point]
        gamete_two = individualtwo.chromosome[crossover_point:]
        # Check union of gametes
        child_gamete = population.mate(gamete_one, gamete_two, individualone, individualtwo)
        self.list_of_individuals.append(individual(child_gamete))
        return individual(child_gamete)

    def run_population(self):
        """
        Runs this population for self.num_generations, crossing over parents using self.crossover.
        Returns: The best individual of this population.

        """
        for _ in range(self.num_generations):
            #Get suitable parents
            parentslist = self.get_suitable_parents()
            #Get the current best
            current_best = self.return_best_individual()
            for pairing in parentslist:
                #do -> crossover the parents genome.
                parentone = pairing[0]
                parenttwo = pairing[1]
                child = self.crossover(parentone, parenttwo)
                if child.fitness > current_best.fitness:
                    print("New Best solution found! Best profit(fitness) is {}".format(child.fitness))
            self.best_individual = self.return_best_individual()
        return self.return_best_individual()

    @staticmethod
    def mate(gamete_one: list, gamete_two: list, individualone, individualtwo):
        """
        Task cannot exist twice in one day. If it happens that one task gets put in the front half of
        individualone's solution, and in the second half of individualtwo's solution, we have to delete one.
        If individual one's solution is better (higher fitness), delete the duplicate from individual two.
        And vice versa if individual two's solution is better.
        Args:
            gamete_one:
                slice of individualone's chromosome around crossover point.
            gamete_two:
                slice of individualtwo's chromosome around crossofer point.
            individualone:
                individualone -- an individual from our population.
            individualtwo:
                individualtwo -- an individual from our population.

        Returns:
            merged chromosome of the parents.
        """
        for i in range(0, len(gamete_one) - 1):
            for j in range(0, len(gamete_two) - 2):
                try:
                    if gamete_one[i].get_task_id() == gamete_two[j].get_task_id():
                        if individualone.fitness >= individualtwo.fitness:
                            gamete_two.pop(j)
                        else:
                            gamete_one.pop(i)
                except IndexError as e:
                    print(str(len(gamete_one)) + ", " + str(i) + "\n" + str(len(gamete_two)) + ", " + str(j))


        return gamete_one + gamete_two


class individual:
    """
    An individual, with a potential task list as its chromosome.
    """
    def __init__(self, my_list_of_tasks):
        """
        Sets the chromosome of this individual to be a list of tasks, either from crossover (above)
        or random input.
        Args:
            my_list_of_tasks: A list of Task objects, in order.
        """
        self.chromosome = my_list_of_tasks
        self.fitness = None
        self.get_fitness()

    def get_fitness(self):
        """
        Evaluates the total profit gained from the ordering of tasks outlined in self.chromosome
        Returns:
            The fitness of this chromosome (float).
        """
        total_reward = 0
        time = 0
        for task in self.chromosome:
            if time >= 1440:
                break
            # Time to complete the task
            time += task.duration
            # Check if task is late
            if task.deadline <= time:
                total_reward += task.get_late_benefit(time - task.deadline)
            # If not late, then get full reward
            else:
                total_reward += task.get_max_benefit()
        self.fitness = total_reward
        return total_reward

    def dump_results(self, outputloc):
        """
        Writes list of tasks to output location described in the population.
        Returns:
            Nothing, but writes file to outputloc described in population.

        """
        output_list = []
        for i in range(len(self.chromosome)):
            output_list.append(self.chromosome[i].get_task_id())
        write_output_file(outputloc, output_list)

    def __str__(self):
        """
        String representation of individual, for debugging and pretty printing.
        Returns: str, with the profit gained by this ordering of tasks, and the length of the chromosome (how many tasks we have completed).

        """
        return "Individual with profit {}, using {} tasks.".format(self.fitness, len(self.chromosome))



def solve(input_file_location):

    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """


    trialpopulation = population(input_file_location, 10000, 5000)
    best_individual = trialpopulation.run_population()
    return best_individual


def write_multiple_inputs(length_of_input):
    tasklist = [Task(i + 1, int(random.randint(1, 1440)), random.randint(1, 60), round(random.uniform(10.0, 100.0), 3))
                for i in range(length_of_input)]
    write_input_file("./samples/" + str(length_of_input) + ".in", tasklist)


def convert_output_to_list_of_tasks(ordering: list, tasklist: list):
    """
    Takes output file and generates task list. For use in comparing to staff solution.
    Args:
        ordering: read from output file.
        tasklist: tasklist from corresponding input file.

    Returns:
        List of Task objects, in order of their completion in the staff output file.

    """
    outputlist = []
    for task_id in ordering:
        for task in tasklist:
            if task_id == task.get_task_id():
                outputlist.append(task)
    return outputlist



# Here's an example of how to run your solver.
# if __name__ == '__main__':
#     for size in os.listdir('inputs/'):
#         if size not in ['small', 'medium', 'large']:
#             continue
#         for input_file in os.listdir('inputs/{}/'.format(size)):
#             if size not in input_file:
#                 continue
#             input_path = 'inputs/{}/{}'.format(size, input_file)
#             output_path = 'outputs/{}/{}.out'.format(size, input_file[:-3])
#             print(input_path, output_path)
#             tasks = read_input_file(input_path)
#             output = solve(tasks)
#             write_output_file(output_path, output)
#     for input_path in os.listdir('inputs/'):
#         output_path = 'outputs/' + input_path[:-3] + '.out'
#         tasks = read_input_file(input_path)
#         output = solve(tasks)
#         write_output_file(output_path, output)
"""
tasks = read_input_file("samples/100.in")
stafftasks = read_output_file("samples/100.out")

benchmark = individual(convert_output_to_list_of_tasks(stafftasks, tasks))
print("Staff solution has {}".format(benchmark))

result = solve("samples/100.in")
result.dump_results()
print(result)
if benchmark.fitness <= result.fitness:
    print("We just beat the staff solution, by a margin of ${}".format(result.fitness - benchmark.fitness))
"""
def get_list_of_files(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_list_of_files(fullPath)
        else:
            if ".in" in entry:
                allFiles.append(fullPath)
    return allFiles


if __name__ == '__main__':
    list_of_files = get_list_of_files("inputs/")
    for input_path in list_of_files:
        output_path = 'outputs/' + input_path.split("/")[1]  + "/" + input_path.split("/")[2].split(".")[0] + ".out"
        result = solve(input_path)
        result.dump_results(output_path)
