"""Common plotting methods.

.. deprecated:: 0
   Randomness test results will  use `Altair` in the future"""
import matplotlib.pyplot as plt
import numpy as np
from numpy import inf
from scipy.special import erfc
from scipy.special import gammaincc
from scipy.special import logit
from scipy.stats import chi2

__all__ = ["plot_erfc", "plot_chi2", "plot_gammaincc", "range_annotation"]


def plot_erfc(statistic):
    fig, ax = plt.subplots()

    x = np.linspace(-3, 3)

    ax.plot(x, erfc(x))
    ax.axvline(statistic, color="black")

    return fig


def plot_chi2(statistic, df):
    fig, ax = plt.subplots()

    x = np.linspace(0, max(statistic + 1, 4))

    ax.plot(x, chi2.pdf(x, df))

    statistic_pdf = chi2.pdf(statistic, df)
    ax.axvline(statistic, color="black")
    ax.set_ylim([0, statistic_pdf])

    return fig


def plot_gammaincc(statistic, boundary):
    fig, ax = plt.subplots()

    x = np.linspace(0, 4)

    ax.plot(x, gammaincc(boundary, x))
    ax.axvline(statistic, color="black")

    return fig


def range_annotation(ax, xmin, xmax, ymin, text, scale=0.01):
    width = xmax - xmin
    peak = 6 * scale
    margin = peak / 2

    # --------------
    # Generate plots
    # --------------

    logit_x = np.linspace(0, 1)
    logit_y = logit(logit_x)

    # Convert unplottable infinity values into the apexes
    half_y = logit_y * scale
    half_y[half_y == -inf] = -peak
    half_y[half_y == inf] = peak

    half_y = half_y + ymin + peak + margin
    half_x = logit_x * (width / 2) + xmin

    x = np.concatenate([half_x, half_x + (width / 2)])
    y = np.concatenate([half_y, half_y[::-1]])

    ax.plot(x, y, color="black")

    # ----
    # Text
    # ----

    ax.text(half_x[-1], half_y[-1] + margin, text, ha="center")
