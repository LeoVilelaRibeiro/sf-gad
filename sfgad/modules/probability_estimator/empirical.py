import pandas as pd
import numpy as np

from .probability_estimator import ProbabilityEstimator


class Empirical(ProbabilityEstimator):

    def __init__(self, direction='right-tailed'):

        if direction not in ['right-tailed', 'left-tailed', 'two-tailed']:
            raise ValueError("The given direction for probability calculation is not known! "
                             "Possible directions are: 'right-tailed', 'left-tailed' & 'two-tailed'.")

        self.direction = direction

    def estimate(self, vertex_name, features_values, reference_features_values, weights):
        """
        Takes a vertex and a reference to the database.
        Returns a list of p_values with a p_value for each given feature value in features_values. These p_values are
        calculated based on the given reference_features_values.
        :param vertex_name: the name of the vertex.
        :param features_values: Dataframe with values of features.
        :param reference_features_values: List of tuples of windows and the corresponding feature values.
        :param weights: the weights for the different windows.
        :return: List of p_values.
        """

        # Add the weights to a combined dataframe of reference_values and weights
        df = pd.merge(reference_features_values, weights, on="time_window")

        # Get a list of all the features for building an easy iterable
        features_list = features_values.columns.values.tolist()
        features_list.remove('name')

        p_values_list = []

        for feature_name in features_list:

            # This is the feature value for the current feature of the vertex in question
            feature_value = features_values.iloc[0][feature_name]

            if self.direction == 'two-tailed':
                p_value_right = self.empirical(feature_value, df[feature_name], df['weight'], 'right')
                p_value_left = self.empirical(feature_value, df[feature_name], df['weight'], 'left')

                p_value = 2 * min(p_value_right, p_value_left)

            else:
                p_value = self.empirical(feature_value, df[feature_name], df['weight'], self.direction)

            # Add the calculated p_value to the list of p_values for this vertex
            p_values_list.append(p_value)

        # Return the completed list
        return p_values_list

    def empirical(self, value, references, weights, direction):
        """
        Execute the empirical p-value calculation.
        :param value: the given minimal p-value
        :param references: the minimal p_values of the reference observations
        :param weights: weights for the reference observations
        :param direction: direction for the empirical calculation.
        :return: the empirical p_value
        """
        isnan = np.isnan(references)

        if direction == 'right-tailed':
            conditions = references[~isnan] >= value
        elif direction == 'left-tailed':
            conditions = references[~isnan] <= value
        else:
            raise ValueError("The given direction for empirical calculation is not known.")

        sum_all_weights = weights[~isnan].sum()
        sum_conditional_weights = (conditions * weights[~isnan]).sum()

        if sum_all_weights == 0:
            return np.nan

        return sum_conditional_weights / sum_all_weights