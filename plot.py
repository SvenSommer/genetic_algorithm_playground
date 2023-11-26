import random
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def plot_strategie_value_over_generations(generation_data, generations):
    plt.figure(figsize=(10, 6))

    for generation in range(generations):
        plt.scatter(
            [generation] * len(generation_data[generation]),
            generation_data[generation],
            label=f"Gen {generation + 1}",
        )

    plt.title("Evolution of Strategie Value Across Generations")
    plt.xlabel("Generation")
    plt.ylabel("Strategie Value")
    plt.legend()
    plt.show()

def smooth_data(data, window_size):
    """ Smooths the data using a moving average. """
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def plot_average_variation(generation_data, generations, attempts_data, window_size=5):
    # Calculate the average Strategie Values for each generation
    average_strategie_values = [sum(generation) / len(generation) for generation in generation_data]
    # Calculate the standard deviation of Strategie Values for each generation
    std_strategie_values = [np.std(generation) for generation in generation_data]
    # Calculate the average of attempts for each generation
    average_attempts = [sum(attempts) / len(attempts) for attempts in attempts_data]
    # Smoothing the average attempts
    smoothed_attempts = smooth_data(average_attempts, window_size)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Strategie Value', color=color)
    ax1.plot(range(generations), average_strategie_values, label="Average Strategie Value", color=color)
    ax1.fill_between(range(generations), 
                     [average - std for average, std in zip(average_strategie_values, std_strategie_values)], 
                     [average + std for average, std in zip(average_strategie_values, std_strategie_values)], 
                     color="lightblue", alpha=0.5)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # Second y-axis for the average attempts
    color = 'tab:red'
    ax2.set_ylabel('Average Attempts (Smoothed)', color=color)  
    ax2.plot(range(window_size - 1, generations), smoothed_attempts, label="Average Attempts (Smoothed)", color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # For a clean layout
    plt.title("Average and Variation of Strategie Value Over Generations with Average of Attempts (Smoothed)")
    plt.show()

    return fig

def plot_randomness(target_numbers):
    fig = plt.figure(figsize=(12, 6))
    generations = list(range(1, len(target_numbers) + 1))

    plt.scatter(generations, target_numbers, alpha=0.7)
    plt.title("Target Numbers per Generation")
    plt.xlabel("Generation")
    plt.ylabel("Target Number")
    plt.grid(True)

    return fig
