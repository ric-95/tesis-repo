Paraview Extractor
===================

Script for extracting data from ParaView given a configuration file in JSON
format.

Configuration Template
----------------------

```javascript
{"planes": [
    {"origin": [x0, y0, z0],
    "point1": [x1, y1, z1],
    "point2": [x2, y2, z2],
    "x_res": x_res,
    "y_res": y_res,
    "timestep": timestep,
    "variables": [var1, var2, ...],
    "output": output_path}, ...],
 "lines": [
     {"point1": [x1, y1, z1],
      "point2": [x2, y2, z2],
      "resolution": resolution,
      "timestep": timestep,
      "variables": [var1, var2, ...],
      "output": output_path}, ...]}
```

Given the relatively simple structure of the configuration needed, one can
produce with ease an arbitrarily large amount of planes and lines with simple
scripts.

A sample of such scripts are found in the `bin` directory.
