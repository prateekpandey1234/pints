#
# MCMC result object
#
# This file is part of PINTS.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the PINTS
#  software package.
#
# Some code in this file was adapted from Myokit (see http://myokit.org)
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals
import pints._diagnostics as diagnostics
import numpy as np
from tabulate import tabulate


class MCMCResults(object):
    """
    Wrapper class calculates key summaries of posterior samples and diagnostic
    quantities from MCMC chains. These include the posterior mean, standard
    deviation, quantiles, rhat and effective sample size.
    """

    def __init__(self, chains, time=None, parameter_names=None):
        self._chains = chains
        self._num_params = chains[0].shape[1]
        if time is not None and float(time) <= 0:
            raise ValueError('Elapsed time must be positive.')
        self._time = time
        if parameter_names is not None and (
                self._num_params != len(parameter_names)):
            raise ValueError(
                'Parameter names list must be same length as number of ' +
                'sampled parameters')
        if parameter_names is None:
            parameter_names = (
                ["param " + str(i + 1) for i in range(self._num_params)])
        self._parameter_names = parameter_names
        self._summary_list = []

    def chains(self):
        """
        Returns posterior samples from all chains separately.
        """
        return self._chains

    def mean(self):
        """
        Return the posterior means of all parameters.
        """
        return self._mean

    def std(self):
        """
        Return the posterior standard deviation of all parameters.
        """
        return self._std

    def quantiles(self):
        """
        Return the 2.5%, 25%, 50%, 75% and 97.5% posterior quantiles.
        """
        return self._quantiles

    def rhat(self):
        """
        Return Gelman and Rubin's [1] rhat value as defined in [1]_.

        [1] "Inference from iterative simulation using multiple
        sequences", 1992, Gelman and Rubin, Statistical Science.
        """
        return self._rhat

    def ess(self):
        """
        Return the effective sample size for each parameter as defined in [2]_.

        [2] "Bayesian data analysis", 3rd edition, 2014, Gelman et al.,
        CRC Press.
        """
        return self._ess

    def ess_per_second(self):
        """
        Return the effective sample size (as defined in [2]_) per second of run
        time for each parameter.

        [2] "Bayesian data analysis", 3rd edition, 2014, Gelman et al.,
        CRC Press.
        """
        return self._ess_per_second

    def make_summary(self):
        """
        Calculates posterior summaries for all parameters.
        """
        stacked = np.vstack(self._chains)
        self._mean = np.mean(stacked, axis=0)
        self._std = np.std(stacked, axis=0)
        self._quantiles = np.percentile(stacked, [2.5, 25, 50,
                                                  75, 97.5], axis=0)
        self._ess = diagnostics.effective_sample_size(stacked)
        if self._time is not None:
            self._ess_per_second = np.array(self._ess) / self._time
        self._num_chains = len(self._chains)

        # If there is more than 1 chain calculate rhat
        # otherwise return NA
        if self._num_chains > 1:
            self._rhat = diagnostics.rhat_all_params(self._chains)
        else:
            self._rhat = np.repeat("NA", self._num_params)

        if self._time is not None:
            for i in range(0, self._num_params):
                self._summary_list.append([self._parameter_names[i],
                                           self._mean[i],
                                           self._std[i],
                                           self._quantiles[0, i],
                                           self._quantiles[1, i],
                                           self._quantiles[2, i],
                                           self._quantiles[3, i],
                                           self._quantiles[4, i],
                                           self._rhat[i],
                                           self._ess[i],
                                           self._ess_per_second[i]])
        else:
            for i in range(0, self._num_params):
                self._summary_list.append(["param " + str(i + 1),
                                           self._mean[i],
                                           self._std[i],
                                           self._quantiles[0, i],
                                           self._quantiles[1, i],
                                           self._quantiles[2, i],
                                           self._quantiles[3, i],
                                           self._quantiles[4, i],
                                           self._rhat[i],
                                           self._ess[i]])

    def summary(self):
        """
        Return a list of the parameter name, posterior mean, posterior std
        deviation, the 2.5%, 25%, 50%, 75% and 97.5% posterior quantiles,
        rhat, effective sample size (ess) and ess per second of run time.
        """
        if self._summary_list == []:
            self.make_summary()
        return self._summary_list

    def print_summary(self):
        """
        Prints posterior summaries for all parameters to the console, including
        the parameter name, posterior mean, posterior std deviation, the
        2.5%, 25%, 50%, 75% and 97.5% posterior quantiles, rhat, effective
        sample size (ess) and ess per second of run time.
        """
        if self._summary_list == []:
            self.make_summary()
        if self._time is not None:
            print(tabulate(self._summary_list,
                  headers=["param", "mean", "std.",
                           "2.5%", "25%", "50%",
                           "75%", "97.5%", "rhat",
                           "ess", "ess per sec."],
                  numalign="left", floatfmt=".2f"))
        else:
            print(tabulate(self._summary_list,
                  headers=["param", "mean", "std.",
                           "2.5%", "25%", "50%",
                           "75%", "97.5%", "rhat",
                           "ess"],
                  numalign="left", floatfmt=".2f"))

    def extract(self, param_number):
        """
        Extracts posterior samples for a given parameter number.
        """
        stacked = np.vstack(self._chains)
        return stacked[:, param_number]

    def extract_all(self):
        """
        Return the posterior samples for all parameters.
        """
        return np.vstack(self._chains)

    def time(self):
        """
        Return the run time taken for sampling.
        """
        return self._time
