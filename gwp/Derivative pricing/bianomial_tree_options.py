import numpy as np


def binomial_tree_option(S0, K, T, r, u, d, steps):
    size = steps + 1
    dt = T / steps
    p = (np.exp(r * dt) - d) / (u - d)
    ud_tree = np.zeros([size, size])
    eu_put_tree = np.zeros([size, size])
    eu_call_tree = np.zeros([size, size])
    am_put_tree = np.zeros([size, size])
    am_call_tree = np.zeros([size, size])

    print(dt, r, p)
    for i in range(size):
        for j in range(size - i):
            underlying_price = S0 * u ** j * d ** i
            ud_tree[i][j] = underlying_price
            if i + j == steps:
                eu_call_tree[i][j] = max(underlying_price - K, 0)
                eu_put_tree[i][j] = max(K - underlying_price, 0)
                am_call_tree[i][j] = max(underlying_price - K, 0)
                am_put_tree[i][j] = max(K - underlying_price, 0)

    for i in range(steps - 1, -1, -1):
        for j in range(steps - 1, -1, -1):
            if i + j != steps:
                eu_call_tree[j][i] = np.exp(-r * dt) * (p * eu_call_tree[j, i + 1] + (1 - p) * eu_call_tree[j + 1, i])
                eu_put_tree[j][i] = np.exp(-r * dt) * (p * eu_put_tree[j, i + 1] + (1 - p) * eu_put_tree[j + 1, i])

                am_call_tree[j][i] = np.exp(-r * dt) * (p * am_call_tree[j, i + 1] + (1 - p) * am_call_tree[j + 1, i])
                am_put_tree[j][i] = np.exp(-r * dt) * (p * am_put_tree[j, i + 1] + (1 - p) * am_put_tree[j + 1, i])

                am_call_tree[j][i] = max((ud_tree[j][i] - K), am_call_tree[j][i])
                am_put_tree[j][i] = max((K - ud_tree[j][i]), am_put_tree[j][i])

    return ud_tree, eu_call_tree, eu_put_tree, am_call_tree, am_put_tree


if __name__ == '__main__':
    print(binomial_tree_option(145, 100, 100, 0.1, 1.2, 0.8, 2))