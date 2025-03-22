# SATurday
SATurday – A solver that works (mostly) on weekends.

## Features:

- based on CDCL
- fast and minimal input pre-processing (none)
- dumb literal selection heuristic (set the first unassigned variable to `false`)
- non-randomn restarts (never restarts)
- dumb and expensive indexing techniques
- very basic incrementality (zero)
- conflict analysis with 'decision' criterion (very inefficient)
- basic backjumping (only the bare minumum amount!)
- no clause discharging
