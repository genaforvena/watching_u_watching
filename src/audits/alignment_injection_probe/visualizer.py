import matplotlib.pyplot as plt
import json

def plot_alignment_over_time(results_file):
    """Plot alignment scores across turns"""
    scores = []
    turns = []

    with open(results_file) as f:
        for line in f:
            data = json.loads(line)
            turns.append(data['turn'])
            scores.append(data['alignment_score'])

    plt.plot(turns, scores)
    plt.xlabel('Turn Number')
    plt.ylabel('Alignment Score')
    plt.title('Alignment Degradation Over Time')
    plt.show()
