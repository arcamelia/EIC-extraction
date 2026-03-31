import os
import pandas as pd
import xarray as xr
import numpy as np
from netCDF4 import Dataset

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


def save_eic_csv(times, intensities, output_path):
    df = pd.DataFrame({"time": times, "intensity": intensities})
    df.to_csv(output_path, index=False)
    print(f"Saved EIC CSV: {output_path}")


def extract_multiple_eics(nc_path, output_dir, mz_list, tol_da):
    base = os.path.splitext(os.path.basename(nc_path))[0]
    ds = Dataset(nc_path, "r")

    for mz in mz_list:
        times, eic = extract_eic_from_cdf(ds, mz, tol_da)
        out_file = os.path.join(output_dir, f"{base}_EIC_mz{mz}_tol{tol_da}.csv")
        save_eic_csv(times, eic, out_file)

    ds.close()


def netcdf_to_csv(nc_file, output_dir, variables=None):
    try:
        ds = xr.open_dataset(nc_file)

        if variables:
            available_vars = [v for v in variables if v in ds.data_vars]
            if not available_vars:
                raise ValueError(f"None of the requested variables found in {nc_file}")
            ds = ds[available_vars]
            print(f"Keeping variables: {available_vars}")

        df = ds.to_dataframe().reset_index()

        base_name = os.path.splitext(os.path.basename(nc_file))[0] + ".csv"
        output_path = os.path.join(output_dir, base_name)

        df.to_csv(output_path, index=False)
        print(f"Converted: {nc_file} -> {output_path}")

    except Exception as e:
        print(f"Error processing {nc_file}: {e}")


def batch_convert(input_dir, output_dir, variables=None, mz_list=None, tol_da=0.5):
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith((".nc", ".cdf")):
            path = os.path.join(input_dir, file)

            # convert general variables
            netcdf_to_csv(path, output_dir, variables)

            # extract EICs
            if mz_list:
                extract_multiple_eics(path, output_dir, mz_list, tol_da)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_directory = os.path.join(base_dir, INPUT_DIR)
    output_directory = os.path.join(base_dir, OUTPUT_DIR)

    vars = ["scan_number", "scan_acquisition_time", "total_intensity"]

    # define specific m/z targets for EICs
    mz_targets = [117.1386, 227.1754, 245.1860, 343.3068, 453.3435, 471.3541, 679.5117, 697.5222]
    # mz_targets = [114.0913, 132.1019, 245.1860, 227.1754, 358.2700, 340.2595, 471.3541, 453.3435]
    # ^ EDIT THESE

    # extraction tolerance in Da
    tolerance_da = 0.02

    batch_convert(
        input_directory,
        output_directory,
        variables=vars,
        mz_list=mz_targets,
        tol_da=tolerance_da
    )