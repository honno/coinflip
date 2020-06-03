from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erfc
from scipy.special import gammaincc
from scipy.stats import chi2
from scipy.stats import halfnorm

__all__ = ["plot_halfnorm", "plot_erfc", "plot_chi2", "plot_gammaincc"]

mean = 0
variance = 1
deviation = sqrt(variance)


def plot_halfnorm(x):
    fig, ax = plt.subplots()

    x_axis = np.linspace(0, 3 * deviation)
    normal_dist = halfnorm.pdf(x_axis, mean, deviation)

    ax.plot(x_axis, normal_dist)
    ax.axvline(x, color="black")

    return fig


def plot_erfc(x):
    fig, ax = plt.subplots()

    x_axis = np.linspace(-3, 3)

    ax.plot(x_axis, erfc(x_axis))
    ax.axvline(x, color="black")

    return fig


def plot_chi2(x, df):
    fig, ax = plt.subplots()

    x_axis = np.linspace(0, max(x + 1, 4))

    ax.plot(x_axis, chi2.pdf(x_axis, df))

    y = chi2.pdf(x, df)
    ax.axvline(x, color="black")
    ax.set_ylim([0, y])

    return fig


def plot_gammaincc(x, scale):
    fig, ax = plt.subplots()

    x_axis = np.linspace(0, 4)

    ax.plot(x_axis, gammaincc(scale, x_axis))
    ax.axvline(x, color="black")

    return fig
