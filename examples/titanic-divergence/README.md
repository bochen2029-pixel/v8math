# How far one ulp travels

The motivating case for this repository: a flooding simulation of RMS Titanic (4,408 hull columns,
64 flooded spaces, 290 flow paths, a 0.25 s step, about 9,440 steps to foundering) written in
JavaScript, with a C++/CUDA port that is supposed to reproduce it.

`divergence_data.js` runs the calibrated 1912 scenario twice, as published and with the breach
discharge coefficient moved by exactly one ulp (0.6 to 0.6000000000000001), and records per minute
of simulated time the pitch difference in degrees and the summed difference of the 64 flooded volumes
in cubic metres. When given two golden traces it also compares those; the two included here are the
same run from two machines: `golden_titanic.shipped.json` from the model's author and
`golden_titanic.node24.json` regenerated with Node 24.16 on Windows. They differ in a single hull
opening coordinate by 8.9e-16, one `Math.pow` rounded differently by the two C runtimes.

Both comparisons stay bit-identical for about an hour of simulated time, then the first water flowing
over a bulkhead top turns a one-ulp difference into a visible one. Bulkhead-overtopping times move by
up to 24 s, the final pitch by 0.05 degrees; the foundering time does not move at all.

```
node divergence_data.js <titanic-sim package dir> golden_titanic.shipped.json golden_titanic.node24.json > divergence.csv
python plot_divergence.py divergence.csv ../../docs
```

The package directory must hold the model's `core/core.js` and `core/scenarios.js`: a checkout of the
[Titanic Sinking Simulator](https://github.com/bochen2029-pixel/titanic-sinking-simulator). `divergence.csv`
is the output used for the figure in the top-level README.
