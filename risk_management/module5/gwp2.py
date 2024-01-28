# prompt: implement forward and backward algorithm for hmm optimal sequence  for hidden states without using pgmpy

import numpy as np
import pandas as pd
from collections import defaultdict
from itertools import product

class HMM:
    def __init__(self, n_states):
        self.n_states = n_states
        self.initial_prob = np.zeros(n_states)
        self.transition_prob = np.zeros((n_states, n_states))
        self.emission_prob = np.zeros((n_states, n_states))

    def add_states(self, states):
        self.states = states

    def add_initial_prob(self, state, prob):
        self.initial_prob[self.states.index(state)] = prob

    def add_transition_prob(self, from_state, to_state, prob):
        self.transition_prob[self.states.index(from_state), self.states.index(to_state)] = prob

    def add_emission_prob(self, state, observation, prob):
        self.emission_prob[self.states.index(state), observation] = prob

    def forward_algorithm(self, observations):
        """
        Compute the forward probabilities for the given observations.

        Args:
            observations: A list of observations.

        Returns:
            A numpy array of the forward probabilities.
        """
        T = len(observations)
        N = self.n_states
        alpha = np.zeros((T, N))
        alpha[0, :] = self.initial_prob
        for t in range(1, T):
            for n in range(N):
                alpha[t, n] = np.sum(alpha[t - 1, :] * self.transition_prob[n, :]) * self.emission_prob[n, observations[t]]
        return alpha

    def backward_algorithm(self, observations):
        """
        Compute the backward probabilities for the given observations.

        Args:
            observations: A list of observations.

        Returns:
            A numpy array of the backward probabilities.
        """
        T = len(observations)
        N = self.n_states
        beta = np.zeros((T, N))
        beta[-1, :] = 1.0
        for t in range(T - 2, -1, -1):
            for n in range(N):
                beta[t, n] = np.sum(beta[t + 1, :] * self.transition_prob[:, n]) * self.emission_prob[n, observations[t + 1]]
        return beta

    def optimal_sequence(self, observations):
        """
        Compute the optimal sequence of hidden states for the given observations.

        Args:
            observations: A list of observations.

        Returns:
            A list of the optimal hidden states.
        """
        alpha = self.forward_algorithm(observations)
        beta = self.backward_algorithm(observations)
        T = len(observations)
        N = self.n_states
        gamma = np.zeros((T, N))
        for t in range(T):
            for n in range(N):
                gamma[t, n] = alpha[t, n] * beta[t, n] / np.sum(alpha[-1, :])
        return [np.argmax(gamma[t, :]) for t in range(T)]

if __name__ == "__main__":
    # Create a simple HMM model.
    model = HMM(4)
    model.add_states(['A', 'B', 'C', 'D'])
    model.add_initial_prob('A', 0.5)
    model.add_initial_prob('B', 0.25)
    model.add_initial_prob('C', 0.25)
    model.add_initial_prob('D', 0.0)
    model.add_transition_prob('A', 'A', 0.3)
    model.add_transition_prob('A', 'B', 0.4)
    model.add_transition_prob('A', 'C', 0.3)
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
    observations = [np.random.choice(4, p=model.emission_prob[i, :]) for i in range(4)]
    a = model.forward_algorithm(observations)
    print(a)

    # Compute the optimal sequence of hidden states.
    optimal_sequence = model.optimal_sequence(observations)

    # Print the optimal sequence.
    print(optimal_sequence)
