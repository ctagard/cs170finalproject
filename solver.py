from parse import read_input_file, write_output_file, write_input_file
import os
import random
import collections
from Task import *


class population:
    def __init__(self, list_of_tasks, size_of_population, num_generations):
        self.tasks = list_of_tasks
        self.list_of_individuals = self.get_individuals(size_of_population)
        self.num_generations = num_generations
        self.best_individual = None

    def get_individuals(self, number_of_individuals):
        return [individual(random.sample(self.tasks, random.randint(0, len(self.tasks)))) for _ in
                range(number_of_individuals)]

    def get_fitness_of_population(self):
        best_fitness = {}
        for individual in self.list_of_individuals:
            best_fitness[individual.fitness] = individual
        od = collections.OrderedDict(sorted(best_fitness.items()))
        best_individual_one = od[list(od.keys())[-1]]
        best_individual_two = od[list(od.keys())[-2]]
        return best_individual_one, best_individual_two

    def return_best_individual(self):
        best_fitness = {}
        for individual in self.list_of_individuals:
            best_fitness[individual.fitness] = individual
        od = collections.OrderedDict(sorted(best_fitness.items()))
        best_individual = od[list(od.keys())[-1]]
        return best_individual

    def crossover(self, individualone, individualtwo):
        # Set the crossover point to a uniform random variable in range 1 to the minimum of individual one's chromosome length and individual two's chromosome length
        crossover_point = random.randint(1, min(len(individualone.chromosome), len(individualtwo.chromosome)))
        # Split each chromosome around the crossover point
        gamete_one = individualone.chromosome[:crossover_point]
        gamete_two = individualtwo.chromosome[crossover_point:]
        # Check union of gametes
        child_gamete = population.mate(gamete_one, gamete_two, individualone, individualtwo)
        self.list_of_individuals.append(individual(child_gamete))
        return individual(child_gamete)

    def run_population(self):
        for _ in range(self.num_generations):
            parentone, parenttwo = self.get_fitness_of_population()
            current_best = self.return_best_individual()
            child = self.crossover(parentone, parenttwo)
            if child.fitness > current_best.fitness:
                print("New Best solution found! Best fitness is {}".format(child.fitness))
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
            gamete_two:
            individualone:
            individualtwo:

        Returns:
            merged chromosome of the parents.
        """
        for i in range(0, len(gamete_one) - 1):
            for j in range(0, len(gamete_two) - 1):
                if gamete_one[i].get_task_id() == gamete_two[j].get_task_id():
                    if individualone.fitness >= individualtwo.fitness:
                        gamete_two.pop(j)
                    else:
                        gamete_one.pop(i)

        return gamete_one + gamete_two


class individual:
    def __init__(self, my_list_of_tasks):
        self.chromosome = my_list_of_tasks
        self.fitness = None
        self.get_fitness()

    def get_fitness(self):
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

    def __str__(self):
        return "Individual with fitness {}, using {} tasks.".format(self.fitness, len(self.chromosome))


def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
<<<<<<< HEAD
    return [1]
    pass
=======
    trialpopulation = population(tasks, 1000, 15000)
    best_individual = trialpopulation.run_population()
    return best_individual


def write_multiple_inputs(length_of_input):
    tasklist = [Task(i + 1, int(random.randint(1, 1440)), random.randint(1, 60), round(random.uniform(10.0, 100.0), 3))
                for i in range(length_of_input)]
    write_input_file("./samples/" + str(length_of_input) + ".in", tasklist)
>>>>>>> 7dcc980 (Added back the staff solution of 100.in)


# Here's an example of how to run your solver.
# if __name__ == '__main__':
<<<<<<< HEAD
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
=======
#     for input_path in os.listdir('inputs/'):
#         output_path = 'outputs/' + input_path[:-3] + '.out'
#         tasks = read_input_file(input_path)
#         output = solve(tasks)
#         write_output_file(output_path, output)
tasks = read_input_file("samples/100.in")
result = solve(tasks)
print(result)


>>>>>>> 7dcc980 (Added back the staff solution of 100.in)
