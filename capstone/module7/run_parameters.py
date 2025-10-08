import numpy as np

stop_loss_limits = np.linspace(0, .1, 5)
take_profit_caps = np.linspace(.1, .3, 5)
open_intervals = range(10, 70, 10)

print(f"stop_loss_limits {stop_loss_limits}")
print(f"take_profit_caps {take_profit_caps}")
print(f"open_intervals {list(open_intervals)}")
