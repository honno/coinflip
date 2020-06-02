from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erfc as erfc_
from scipy.special import gammaincc as gammaincc_
from scipy.stats import chi2 as chi2_
from scipy.stats import halfnorm as halfnorm_

__all__ = ["halfnorm", "erfc", "chi2", "gammaincc"]

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


def chi2(x, df):
    fig, ax = plt.subplots()

    x_axis = np.linspace(0, max(x + 1, 4))

    ax.plot(x_axis, chi2_.pdf(x_axis, df))

    y = chi2_.pdf(x, df)
    ax.axvline(x, color="black")
    ax.set_ylim([0, y])

    return fig


def gammaincc(x, scale):
    fig, ax = plt.subplots()

    x_axis = np.linspace(0, 4)

    ax.plot(x_axis, gammaincc_(scale, x_axis))
    ax.axvline(x, color="black")

    return fig
