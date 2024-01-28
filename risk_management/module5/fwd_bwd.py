# prompt: implement forward and backward algorithm for hmm optimal sequence  for hidden states

from collections import defaultdict
from itertools import product
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from pgmpy.models import HMM
from pgmpy.factors.discrete import TabularCPD

class ForwardBackward(object):

    def __init__(self, model: HMM):
        self.model = model

    def forward(self, observations: List[int]):
        """
        Compute the forward probabilities for the given observations.

        Args:
            observations: A list of observations.

        Returns:
            A numpy array of the forward probabilities.
        """
        # Initialize the forward probabilities.
        T = len(observations)
        N = self.model.num_states
        alpha = np.zeros((T, N))
        alpha[0, :] = self.model.initial_prob
        # Compute the forward probabilities.
        for t in range(1, T):
            for n in range(N):
                alpha[t, n] = np.sum(alpha[t - 1, :] * self.model.transition_prob[n, :]) * self.model.emission_prob[n, observations[t]]
        return alpha

    def backward(self, observations: List[int]):
        """
        Compute the backward probabilities for the given observations.

        Args:
            observations: A list of observations.

        Returns:
            A numpy array of the backward probabilities.
        """
        # Initialize the backward probabilities.
        T = len(observations)
        N = self.model.num_states
        beta = np.zeros((T, N))
        beta[-1, :] = 1.0
        # Compute the backward probabilities.
        for t in range(T - 2, -1, -1):
            for n in range(N):
                beta[t, n] = np.sum(beta[t + 1, :] * self.model.transition_prob[:, n]) * self.model.emission_prob[n, observations[t + 1]]
        return beta

    def optimal_sequence(self, observations: List[int]) -> List[int]:
        """
        Compute the optimal sequence of hidden states for the given observations.

        Args:
            observations: A list of observations.

        Returns:
            A list of the optimal hidden states.
        """
        # Compute the forward and backward probabilities.
        alpha = self.forward(observations)
        beta = self.backward(observations)
        # Compute the optimal sequence.
        T = len(observations)
        N = self.model.num_states
        gamma = np.zeros((T, N))
        for t in range(T):
            for n in range(N):
                gamma[t, n] = alpha[t, n] * beta[t, n] / np.sum(alpha[-1, :])
        return [np.argmax(gamma[t, :]) for t in range(T)]

def main():
    # Create a simple HMM model.
    model = HMM(4)
    model.add_states(['A', 'B', 'C', 'D'])
    model.add_transition_prob('A', 'B', 0.3)
    model.add_transition_prob('A', 'C', 0.4)
    model.add_transition_prob('A', 'D', 0.3)
    model.add_transition_prob('B', 'A', 0.2)
    model.add_transition_prob('B', 'B', 0.5)
    model.add_transition_prob('B', 'C', 0.3)
    model.add_transition_prob('C', 'A', 0.3)
    model.add_transition_prob('C', 'B', 0.2)
    model.add_transition_prob('C', 'C', 0.5)
    model.add_transition_prob('D', 'A', 0.5)
    model.add_transition_prob('D', 'B', 0.2)
    model.add_transition_prob('D', 'C', 0.3)
    model.add_emission_prob('A', 0, 0.5)
    model.add_emission_prob('A', 1, 0.3)
    model.add_emission_prob('A', 2, 0.2)
    model.add_emission_prob('B', 0, 0.3)
    model.add_emission_prob('B', 1, 0.5)
    model.add_emission_prob('B', 2, 0.2)
    model.add_emission_prob('C', 0, 0.2)
    model.add_emission_prob('C', 1, 0.3)
    model.add_emission_prob('C', 2, 0.5)
    model.add_emission_prob('D', 0, 0.5)
    model.add_emission_prob('D', 1, 0.2)
    model.add_emission_prob('D', 2, 0.3)

    # Generate some observations from the model.
    observations = [np.random.choice(3, p=model.emission_prob[i, :]) for i in range(10)]

    # Compute the optimal sequence of hidden states.
    fb = ForwardBackward(model)
    optimal_sequence = fb.optimal_sequence(observations)

    # Print the optimal sequence.
    print(optimal_sequence)

if __name__ == '__main__':
    main()

