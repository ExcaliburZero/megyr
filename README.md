# Megyr [![Build Status](https://travis-ci.org/ExcaliburZero/megyr.svg?branch=master)](https://travis-ci.org/ExcaliburZero/megyr) [![Documentation Status](https://readthedocs.org/projects/megyr/badge/?version=latest)](https://megyr.readthedocs.io/en/latest/?badge=latest)
Megyr is a Python library for creating scripts to automate MESA and GYRE runs over grids of parameter values. It provides a main function that you can run with a set of configuration settings to determine how to run MESA and GYRE and what values to use for the different models.

```python
import megyr

def main():
    megyr.run({
        "input": {
            "mesa_configs": ["inlist.mustache"],
            "gyre_config": "gyre.in.mustache"
        },
        "output": {
            "output_dir": "out",
            "mesa_profile_summary_file": "mesa_profile_attributes.csv",
            "gyre_oscillations_summary_file": "oscillations.csv"
        },
        "settings": {
            "mesa_star_location": "star",
            "gyre_location": "$GYRE_DIR/bin/gyre",
        },
        "stages": {
            "mesa_params": mesa_params,
            "gyre_params": calc_gyre_params,
        }
    })

mesa_params = {
    "initial_mass": [1, 1.1, 1.5],
    "y": [0.25, 0.27, 0.32]
}

def calc_gyre_params(mesa_params, mesa_data):
    return {
        "l": [0, 1, 2],

        # Look at all the profiles that are at least 1 Gyr in age
        "profile": mesa_data[mesa_data["star_age"] > 1000000000]["profile"]
    }

if __name__ == "__main__":
    main()
```
