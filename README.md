# SmithWagnerCV
 
This module produces critical values for the disaggregated learning types as described in Smith and Wagner (2018) and Smith and White (2019 - unpublished). 

## Examples

Run a Monte Carlo Simulation of mu value of 0.1 and 25 students.

```python
from SmithWagnerCV import RunSimulation

d = RunSimulation(25, 0.1)

```

Simulate all combinations of [10,20] students and [0.1,0.5] mu values and return them as a dictionary

```python
from SmithWagnerCV import SimulationTable

d = SimulateTable([10,20], [0.1,0.5])

```
Simulate all combinations of [10,20] students and [0.1,0.5] mu values and save them to CSV files

```python
from SmithWagnerCV import SaveSimulationTable 

d = SaveSimulationTable([10,20], [0.1,0.5])

```