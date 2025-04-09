import pyPRISMClimate as ppc
import os

# --- Configuration ---
start_year = 2010
end_year = 2023
years = list(range(start_year, end_year + 1))
months = list(range(1, 12 + 1))
output_directory = 'Monthly_Ave_Temp'

# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# --- Download Data ---
print(f"Downloading monthly mean temperature data ...")

try:
    ppc.get_prism_monthlys(
        variable='tmean',
        years=years,
        months=months,
        dest_path=output_directory,
        # keep_zip=False  # Crashing when set to True, need to delete zip folders manually
    )
    print("Download complete!")
    print(f"Files saved in: {output_directory}")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure you have the pyPRISMClimate library installed and that your internet connection is stable.")

print("Script finished.")