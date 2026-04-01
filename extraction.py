import os
import pandas as pd
import xarray as xr
import numpy as np
from netCDF4 import Dataset

MZ_TARGETS_PA66 = [117.1386, 227.1754, 245.1860, 343.3068, 453.3435, 471.3541, 679.5117, 697.5222]
MZ_TARGETS_PA6 = [114.0913, 132.1019, 245.1860, 227.1754, 358.2700, 340.2595, 471.3541, 453.3435]

TOLERANCE_DA = 0.02


def extract_eics(input_file, output_dir, mz_list):
    """
    Extract EICs from `input_file` based on all m/z values provided in list.
    """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    out_file = os.path.join(output_dir, f"{base_name}_EICs.csv")
    ds = Dataset(input_file, "r")

    scan_idx = ds.variables["scan_index"][:]
    times = ds.variables["scan_acquisition_time"][:]
    mass_vals = ds.variables["mass_values"][:]
    intensity_vals = ds.variables["intensity_values"][:]

    num_scans = len(scan_idx)
    mz_bounds = [(mz - TOLERANCE_DA, mz + TOLERANCE_DA) for mz in mz_list]
    eic_matrix = np.zeros((num_scans, len(mz_list)))

    for i in range(num_scans):
        start = scan_idx[i]
        end = scan_idx[i+1] if i < num_scans - 1 else len(mass_vals)

        scan_mz = mass_vals[start:end]
        scan_int = intensity_vals[start:end]

        # compute all mz targets for current scan
        for j, (low, high) in enumerate(mz_bounds):
            mask = (scan_mz >= low) & (scan_mz <= high)
            eic_matrix[i, j] = scan_int[mask].sum()

    ds.close()

    # build dataframe and write it to csv
    df = pd.DataFrame(eic_matrix, columns=[f"mz_{mz:.4f}" for mz in mz_list])
    df.insert(0, "time", times)
    df.to_csv(out_file, index=False)
    print(f"Saved combined EIC CSV: {out_file}")


def batch_convert(input_dir, output_dir):
    """
    Convert all .CDF files in `input_dir` to .CSV files in `output_dir`.\n
    Expects file names to start with either 'PA66' or 'PA6'.
    """
    for file in os.listdir(input_dir):
        if file.lower().endswith((".nc", ".cdf")):
            input_file = os.path.join(input_dir, file)

            # choose targets based on PA substrate indicated in file name
            if file.upper().startswith("PA66"):
                mz_list = MZ_TARGETS_PA66
            else:
                mz_list = MZ_TARGETS_PA6
            
            extract_eics(input_file, output_dir, mz_list)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    batch_convert(input_dir, output_dir)