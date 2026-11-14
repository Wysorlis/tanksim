"""Check ideal tank drainage against the integrated Torricelli equation."""

from math import pi, sqrt

import pytest

from tanksim.boundaries import Atmosphere
from tanksim.constants import GRAVITY
from tanksim.link import Link
from tanksim.models import Orifice
from tanksim.simulation import Simulation
from tanksim.tank import Geometry, Port, Tank


INITIAL_LEVEL = 1.0  # m
TANK_SURFACE = 1.0  # m²
ORIFICE_SECTION = 0.1  # m²
END_TIME = 2.0  # s; before half the analytical emptying time (~4.52 s).
TIME_STEPS = (0.1, 0.05, 0.025)


def analytical_level(time: float) -> float:
    # dh/dt = -(a / S) * sqrt(2 * g * h), with equal surface pressures.
    root_level = (
        sqrt(INITIAL_LEVEL)
        - ORIFICE_SECTION / TANK_SURFACE * sqrt(GRAVITY / 2.0) * time
    )
    return max(0.0, root_level) ** 2


@pytest.fixture(scope="module")
def drainage_histories():
    histories = {}

    for dt in TIME_STEPS:
        tank = Tank("TANK")
        tank.set_geometry(Geometry(height=1.5, surface=TANK_SURFACE))
        tank.set_level(INITIAL_LEVEL)

        link = Link(
            name="DRAIN",
            upstream=Port(tank, 0.0),
            downstream=Atmosphere(),
            model=Orifice(diameter=sqrt(4.0 * ORIFICE_SECTION / pi)),
        )

        simulation = Simulation(tanks=[tank], links=[link])
        simulation.dt = dt
        simulation.setup()
        link.open()

        history = [(simulation.time, tank.level)]
        for _ in range(round(END_TIME / dt)):
            simulation.step()
            history.append((simulation.time, tank.level))

        histories[dt] = history

    return histories


@pytest.mark.parametrize("dt", TIME_STEPS)
def test_drainage_level_matches_analytical_solution(drainage_histories, dt):
    history = drainage_histories[dt]

    assert history[-1][0] == pytest.approx(END_TIME)
    assert all(level > 0.0 for _, level in history)

    maximum_error = max(
        abs(level - analytical_level(time)) for time, level in history
    )
    # Allow 1% of the initial level at dt=0.1 s, scaled with the time step.
    error_budget = 0.01 * INITIAL_LEVEL * dt / TIME_STEPS[0]
    assert maximum_error <= error_budget, (
        f"dt={dt}: maximum level error {maximum_error:g} m "
        f"exceeds {error_budget:g} m"
    )


def test_drainage_converges_with_time_step_refinement(drainage_histories):
    exact_final_level = analytical_level(END_TIME)
    errors = []

    for dt in TIME_STEPS:
        time, level = drainage_histories[dt][-1]
        assert time == pytest.approx(END_TIME)
        errors.append(abs(level - exact_final_level))

    for coarse_error, fine_error in zip(errors, errors[1:]):
        # First-order Euler convergence gives a ratio near 0.5. Allow margin
        # for finite steps and accept faster convergence from a future solver.
        assert fine_error <= 0.6 * coarse_error, (
            f"Halving dt reduced the final level error from {coarse_error:g} "
            f"to {fine_error:g} m; expected at least a 40% reduction"
        )
