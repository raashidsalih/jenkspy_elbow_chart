# -*- coding: utf-8 -*-
import warnings
from collections.abc import Iterable
from math import isfinite
from . import jenks

try:
    import numpy as np
except ImportError:
    np = None

class JenksNaturalBreaks:
    def __init__(self, nb_class=6):
        self.nb_class = nb_class
        
    def fit(self, x):
        self.breaks_ = jenks_breaks(x, self.nb_class)
        self.inner_breaks_ = self.breaks_[1:-1] # because inner_breaks is more
        if np:
            self.labels_ = self.predict(x)
            self.groups_ = self.group(x)
        else:
            import warnings
            warnings.warn("No numpy module found. JenksNaturalBreaks interface only generate breaks_ and inner_breaks_")
        
    def predict(self, x):
        if np.size(x) == 1:
            return np.array(self.get_label_(x, idx=0))
        else:
            labels_ = []
            for val in x:
                label_ = self.get_label_(val, idx=0)
                labels_.append(label_)
            return np.array(labels_)
        
    def group(self, x):
        x = np.array(x)
        groups_ = [x[x <= self.inner_breaks_[0]]]
        for idx in range(len(self.inner_breaks_))[:-1]:
            groups_.append(x[(x > self.inner_breaks_[idx]) * (x <= self.inner_breaks_[idx+1])])  
        groups_.append(x[x > self.inner_breaks_[-1]])
        return groups_
    
    def goodness_of_variance_fit(self, x):
        x = np.array(x)
        array_mean = np.mean(x)
        sdam = sum([(value - array_mean)**2 for value in x])
        sdcm = 0
        for group in self.groups_:
            group_mean = np.mean(group)
            sdcm += sum([(value - group_mean)**2 for value in group])
        gvf = (sdam - sdcm)/sdam
        return gvf

    def get_label_(self, val, idx=0):
        try:
            if val <= self.inner_breaks_[idx]:
                return idx
            else:
                idx = self.get_label_(val, idx+1)
                return idx
        except:
            return len(self.inner_breaks_)

def jenks_breaks(values, nb_class):
    """
    Compute jenks natural breaks on a sequence of `values`, given `nb_class`,
    the number of desired class.

    Parameters
    ----------
    values : array-like
        The Iterable sequence of numbers (integer/float) to be used.
    nb_class : int
        The desired number of class (as some other functions requests
        a `k` value, `nb_class` is like `k` + 1). Have to be lesser than
        the length of `values` and greater than 2.

    Returns
    -------
    breaks : tuple of floats
        The computed break values, including minimum and maximum, in order
        to have all the bounds for building `nb_class` class,
        so the returned tuple has a length of `nb_class` + 1.


    Examples
    --------
    Using nb_class = 3, expecting 4 break values , including min and max :

    >>> jenks_breaks(
            [1.3, 7.1, 7.3, 2.3, 3.9, 4.1, 7.8, 1.2, 4.3, 7.3, 5.0, 4.3],
            nb_class = 3)  # Should output (1.2, 2.3, 5.0, 7.8)

    """

    if not isinstance(values, Iterable) or isinstance(values, (str, bytes)):
        raise TypeError("A sequence of numbers is expected")
    if isinstance(nb_class, float) and int(nb_class) == nb_class:
        nb_class = int(nb_class)
    if not isinstance(nb_class, int):
        raise TypeError(
            "Number of class have to be a positive integer: "
            "expected an instance of 'int' but found {}"
            .format(type(nb_class)))

    nb_values = len(values)
    if np and isinstance(values, np.ndarray):
        values = values[np.argwhere(np.isfinite(values)).reshape(-1)]
    else:
        values = [i for i in values if isfinite(i)]
        
    if len(values) != nb_values:
        warnings.warn('Invalid values encountered (NaN or Inf) were ignored')
        nb_values = len(values)
    
    if nb_class >= nb_values or nb_class < 2:
        raise ValueError("Number of class have to be an integer "
                         "greater than 2 and "
                         "smaller than the number of values to use")

    return jenks._jenks_breaks(values, nb_class)
