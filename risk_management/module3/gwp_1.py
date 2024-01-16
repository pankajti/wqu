import numpy as np
import pandas as pd
from pgmpy.estimators import BicScore
from pgmpy.estimators import HillClimbSearch
from pgmpy.estimators import BayesianEstimator
# Generate (discretised) data with dependencies
data = pd.DataFrame(np.random.randint(0, 3, size=(2500, 8)),
columns=list('ABCDEFGH'));
data['A'] += data['B'] + data['C'];
data['H'] = data['G'] - data['A'];
data_train = data[: int(data.shape[0] * 0.75)];
# Learn network structure
hc = HillClimbSearch(data_train);
model = hc.estimate(scoring_method=BicScore(data_train));
# Learn parameters of the network
model._legal
model.fit(data_train,
estimator=BayesianEstimator, prior_type="BDeu");
# Test the dataset
data_test = data[int(0.75 * data.shape[0]) : data.shape[0]];
data_test.drop('A', axis=1, inplace=True); # Drop variable to be predicted
prediction = model.predict(data_test);