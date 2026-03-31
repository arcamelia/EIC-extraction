import os
import pandas as pd
import xarray as xr
import numpy as np
from netCDF4 import Dataset

MZ_TARGETS_PA66 = [117.1386, 227.1754, 245.1860, 343.3068, 453.3435, 471.3541, 679.5117, 697.5222]
MZ_TARGETS_PA6 = [114.0913, 132.1019, 245.1860, 227.1754, 358.2700, 340.2595, 471.3541, 453.3435]

TOLERANCE_DA = 0.02

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def extract_eic_from_cdf(ds, target_mz, tol_da):
    """
    Extract an EIC from a Bruker-exported NetCDF file.
    This reconstructs scans using mass_values + intensity_values + scan_index.
    """
    # essential AIA/MS variables
    mass_values = ds.variables["mass_values"][:]
    intensity_values = ds.variables["intensity_values"][:]
    scan_index = ds.variables["scan_index"][:]

    # time variable may have two possible names
    if "scan_acquisition_time" in ds.variables:
        times = ds.variables["scan_acquisition_time"][:]
    else:
        times = ds.variables["time"][:]

    eic = []

    n_scans = len(scan_index)
    for i in range(n_scans):
        start = scan_index[i]
        end = scan_index[i+1] if i < n_scans - 1 else len(mass_values)

        scan_mz = mass_values[start:end]
        scan_int = intensity_values[start:end]

        mask = (scan_mz >= target_mz - tol_da) & (scan_mz <= target_mz + tol_da)
        eic_intensity = scan_int[mask].sum()

        eic.append(eic_intensity)

    return times, np.array(eic)


def extract_multiple_eics(nc_path, output_dir, mz_list, prefix=""):
    base = os.path.splitext(os.path.basename(nc_path))[0]
    out_file = os.path.join(output_dir, f"{prefix + base}_EICs.csv")
    ds = Dataset(nc_path, "r")

    mass_values = ds.variables["mass_values"][:]
    intensity_values = ds.variables["intensity_values"][:]
    scan_index = ds.variables["scan_index"][:]

    if "scan_acquisition_time" in ds.variables:
        times = ds.variables["scan_acquisition_time"][:]
    else:
        times = ds.variables["time"][:]

    n_scans = len(scan_index)

    # initialize output array: shape (n_scans, n_mz)
    eic_matrix = np.zeros((n_scans, len(mz_list)))

    # precompute bounds for each mz
    mz_bounds = [(mz - TOLERANCE_DA, mz + TOLERANCE_DA) for mz in mz_list]

    # single pass through scans
    for i in range(n_scans):
        start = scan_index[i]
        end = scan_index[i+1] if i < n_scans - 1 else len(mass_values)

        scan_mz = mass_values[start:end]
        scan_int = intensity_values[start:end]

        # compute all mz targets for this scan
        for j, (low, high) in enumerate(mz_bounds):
            mask = (scan_mz >= low) & (scan_mz <= high)
            eic_matrix[i, j] = scan_int[mask].sum()

    ds.close()

    # build df
    df = pd.DataFrame(eic_matrix, columns=[f"mz_{mz:.4f}" for mz in mz_list])
    df.insert(0, "time", times)

    df.to_csv(out_file, index=False)

    print(f"Saved combined EIC CSV: {out_file}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_dir = os.path.join(base_dir, INPUT_DIR)
    output_dir = os.path.join(base_dir, OUTPUT_DIR)

    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith((".nc", ".cdf")):
            path = os.path.join(input_dir, file)

            # choose targets based on PA substrate indicated in file name
            if file.upper().startswith("PA66"):
                mz_list = MZ_TARGETS_PA66
            else:
                mz_list = MZ_TARGETS_PA6
            
            extract_multiple_eics(path, output_dir, mz_list)