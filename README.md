<p align="center">
  <img src="logo/tanksim_minimal_white_blue.png" alt="Logo TANKSIM" width="300">
</p>

# TankSim

TankSim is a small Python solver for 0D incompressible fluid systems.

Systems are built as networks of connected volumes. Volumes hold fluid and exchange it through links representing openings, orifices, breaches, or pumps.

Each volume is described by a single, spatially averaged state. The solver tracks how these states evolve as fluid moves between volumes over time.
