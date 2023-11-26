import random
from plot import plot_average_variation, plot_randomness
from collections import defaultdict
from typing import Tuple, List

import gradio as gr
class Strategy:
    def __init__(self, initial_strategy_range: Tuple[float, float]):
        """ Initialize a strategy with a random value within the given range. """
        self.value = random.uniform(*initial_strategy_range)

    @staticmethod
    def crossover_and_mutate(parent1: 'Strategy', parent2: 'Strategy', mutation_rate: float, mutation_strategy_range: Tuple[float, float]) -> 'Strategy':
        """ Create a child strategy by averaging the values of two parents and possibly mutating. """
        child_value = (parent1.value + parent2.value) / 2
        if random.random() < mutation_rate:
            child_value += random.uniform(*mutation_strategy_range)
        child_value = max(0, min(child_value, 1))
        return Strategy((child_value, child_value))


def initialize_population(size: int, initial_strategie_value_range: Tuple[float, float]) -> List[Strategy]:
    """ Initialize a population of strategies. """
    return [Strategy(initial_strategie_value_range) for _ in range(size)]

def generate_new_population(top_strategies: List[Strategy], mutation_rate: float, mutation_strategie_value_range: Tuple[float, float]) -> List[Strategy]:
    """ Generate a new population from the top strategies through crossover and mutation. """
    return [Strategy.crossover_and_mutate(p1, p2, mutation_rate, mutation_strategie_value_range)
            for i, p1 in enumerate(top_strategies)
            for p2 in top_strategies[i + 1:]]

def evaluate_strategy(strategy: Strategy, target: int, min_range: int, max_range: int, max_attempts: int = 10000) -> int:
    """ Evaluate a strategy by attempting to guess a target number within a range. """
    attempts = 0
    guess = None
    while guess != target and attempts < max_attempts:
        attempts += 1
        guess_range = (max_range - min_range) * strategy.value
        guess = min_range + int(guess_range)
        min_range, max_range = (min_range, guess - 1) if guess > target else (guess + 1, max_range)

    return attempts if guess == target else max_attempts

def select_top_strategies(population, target, min_range, max_range, top_n):
    # Evaluate each strategy in the population and score them
    scored_population = [(strategy, evaluate_strategy(strategy, target, min_range, max_range)) for strategy in population]
    scored_population.sort(key=lambda x: x[1])

    # Ensure that we always return up to top_n strategies, even if they are not ideal
    top_strategies = [strategy for strategy, _ in scored_population[:min(top_n, len(scored_population))]]
    top_scores = [score for _, score in scored_population[:min(top_n, len(scored_population))]]

    return top_strategies, top_scores

def maintain_population_diversity(population, initial_strategie_value, diversity_threshold=0.1):
    # Check if the population lacks diversity in strategy values
    values = [strategy.value for strategy in population]
    if max(values) - min(values) < diversity_threshold:
        # Reinitialize a portion of the population to introduce more diversity
        num_to_reinitialize = len(population) // 2
        for i in range(num_to_reinitialize):
            population[i] = Strategy(initial_strategie_value)

def bucketize_stragie_value(strategie_value, bucket_size=0.01):
    """ Assigns a Strategie Value to a bucket for categorization. """
    return round(strategie_value / bucket_size) * bucket_size

def run_algorithm(max_target_number, generations, population_size, top_n, mutation_rate, min_mutation_step, max_mutation_step, min_initial_strategy, max_initial_strategy):
    # Define ranges for mutation strategy, target number, and initial strategy
    mutation_strategy_range = (min_mutation_step, max_mutation_step)
    target_number_range = (1, max_target_number)
    initial_strategy_range = (min_initial_strategy, max_initial_strategy)

    # Initialize the population
    population = initialize_population(population_size, initial_strategy_range)
    
    # Initialize data collection lists
    target_numbers = []
    max_attempts_data = []
    generation_data = []
    strategy_buckets = defaultdict(int)  # To store the frequency of strategies

    for _ in range(generations):
        # Generate a random target number and add it to the list
        target_number = random.randint(*target_number_range)
        target_numbers.append(target_number)

        # Select top strategies and record their performance
        top_strategies, max_attempts = select_top_strategies(population, target_number, 1, max_target_number, top_n)
        max_attempts_data.append(max_attempts)

        # Generate a new population and maintain its diversity
        population = generate_new_population(top_strategies, mutation_rate, mutation_strategy_range)
        maintain_population_diversity(population, initial_strategy_range)

        # Record strategies for this generation
        generation_data.append([strategy.value for strategy in population])

        # Bucketize strategies for analysis
        for strategy in population:
            bucket = bucketize_stragie_value(strategy.value)
            strategy_buckets[bucket] += 1

    # Determine the most common strategy bucket
    most_common_bucket = max(strategy_buckets, key=strategy_buckets.get)
    most_common_bucket_count = strategy_buckets[most_common_bucket]

    # Generate plots for analysis
    plot = plot_average_variation(generation_data, generations, max_attempts_data)
    randomness_plot = plot_randomness(target_numbers)
    most_common_bucket_info = f"Most Common Strategy: {most_common_bucket} (Count: {most_common_bucket_count})"

    return randomness_plot, plot, most_common_bucket_info


def main():
    with gr.Blocks() as demo:
        gr.Markdown("### Genetic Algorithm and Randomness Visualization")

        with gr.Tab("Genetic Algorithm"):
            with gr.Row():
                with gr.Column():
                    # Basic Settings
                    with gr.Accordion("Basic Settings"):
                        max_target_number = gr.Slider(minimum=1, maximum=1000, value=100, step=1, label="Maximum Target Number")
                        generations = gr.Slider(minimum=5, maximum=10000, value=1000, step=1, label="Generations")
                        population_size = gr.Slider(minimum=3, maximum=1000, value=100, step=1, label="Population Size")
                        top_n = gr.Slider(minimum=3, maximum=100, value=10, step=1, label="Top N")

                    # Advanced Settings
                    with gr.Accordion(label="Advanced Settings", open=False):
                        mutation_rate = gr.Slider(minimum=0, maximum=1, value=0.25, step=0.01, label="Mutation Rate")
                        min_mutation_step = gr.Slider(minimum=-0.2, maximum=0, value=-0.2, step=0.01, label="Minimum Mutation Strategie Value")
                        max_mutation_step = gr.Slider(minimum=0, maximum=0.2, value=0.2, step=0.01, label="Maximum Mutation Strategie Value")
                        min_initial_strategie_value = gr.Slider(minimum=0.1, maximum=0.9, value=0.1, step=0.01, label="Minimum Initial Strategie Value")
                        max_initial_strategie_value = gr.Slider(minimum=0.1, maximum=0.9, value=0.9, step=0.01, label="Maximum Initial Strategie Value")
                    
                    run_button = gr.Button("Run Algorithm")

                with gr.Column():
                    randomness_plot = gr.Plot(label="Randomness Visualization")
                    output_plot = gr.Plot(label="Average and Variance of Strategie Value")
                    output_text = gr.Textbox(label="Most Common Strategie Value")
            
            run_button.click(
                run_algorithm, 
                inputs=[max_target_number, generations, population_size, top_n, mutation_rate, min_mutation_step, max_mutation_step, min_initial_strategie_value, max_initial_strategie_value],
                outputs=[randomness_plot, output_plot, output_text]
            )

    demo.launch()

if __name__ == "__main__":
    main()