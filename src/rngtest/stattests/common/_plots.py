from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erfc as erfc_
from scipy.stats import halfnorm as halfnorm_

mean = 0
variance = 1
deviation = sqrt(variance)


def halfnorm(x):
    fig, ax = plt.subplots()

    x_axis = np.linspace(0, 3 * deviation)
    normal_dist = halfnorm_.pdf(x_axis, mean, deviation)

    ax.plot(x_axis, normal_dist)
    ax.axvline(x, color="black")

    return fig


def erfc(x):
    fig, ax = plt.subplots()

    x_axis = np.linspace(-3, 3)

    ax.plot(x_axis, erfc_(x_axis))
    ax.axvline(x, color="black")

    return fig
