import rasterio as rio
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
import os


precip_directory = 'Monthly_Precip'
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
start_year = 1981
end_year = 2023
years = list(range(start_year, end_year + 1))
output_directory = 'Precip_Aggregates'


def create_file_lists(months, years):
    file_list = []
    for m in months:
        month_list = []
        for y in years:
            file_name = f'PRISM_ppt_stable_4kmM3_{str(y)}{str(m)}_bil.bil'
            month_list.append(file_name)
        file_list.append(month_list)
    print(file_list)
    return file_list


def get_monthly_averages(raster_file_lists):
    for month_list in raster_file_lists:
        raster_arrays = []
        for raster_file in month_list:
            path = os.path.join(precip_directory, raster_file)
            with rio.open(path) as src:
                raster_arrays.append(src.read(1).astype(np.float32))  # Read the first band, convert to float
                profile = src.profile  # Store metadata for output
            summed_array = np.nansum(raster_arrays, axis=0)  # axis zero sums across arrays, axis 1 sums within array
            ave_array = summed_array / len(raster_arrays)
        print(f"Doing Maths for Month {months[raster_file_lists.index(month_list)]}...")

        filename = f'avePPT_month{months[raster_file_lists.index(month_list)]}.tif'
        out_path = os.path.join(output_directory, filename)
        profile.update(dtype=rio.float32, compress='lzw')
        with rio.open(out_path, 'w', **profile) as dst:
            dst.write(ave_array, 1)


def get_annual_average():
    raster_arrays = []
    for m in months:
        file = f'avePPT_month{m}.tif'
        path = os.path.join(output_directory, file)
        with rio.open(path) as src:
            raster_arrays.append(src.read(1).astype(np.float32))
            profile = src.profile
    summed_array = np.nansum(raster_arrays, axis=0)

    profile.update(dtype=rio.float32, compress='lzw')
    outpath = os.path.join(output_directory, 'annual_ppt.tif')
    with rio.open(outpath, 'w', **profile) as dst:
        dst.write(summed_array, 1)

    ave_array = summed_array / len(raster_arrays)
    profile.update(dtype=rio.float32, compress='lzw')
    outpath = os.path.join(output_directory, 'ave_month_ppt.tif')
    with rio.open(outpath, 'w', **profile) as dst:
        dst.write(ave_array, 1)

def calc_seasonality_index():
    month_arrays = []
    for m in months:
        file = f'avePPT_month{m}.tif'
        path = os.path.join(output_directory, file)
        with rio.open(path) as src:
            month_arrays.append(src.read(1).astype(np.float32))

    file = f'annual_ppt.tif'
    path = os.path.join(output_directory, file)
    with rio.open(path) as src:
        annual_array = src.read(1).astype(np.float32)
        profile = src.profile

    file = f'ave_month_ppt.tif'
    path = os.path.join(output_directory, file)
    with rio.open(path) as src:
        ave_month_array = src.read(1).astype(np.float32)


    abs_dev_arrays = []
    for a in month_arrays:
        dif = np.subtract(a, ave_month_array)
        abs = np.absolute(dif)
        abs_dev_arrays.append(abs)
    sum_abs_dev_array = np.nansum(abs_dev_arrays, axis=0)
    SI = sum_abs_dev_array / annual_array

    outpath = os.path.join(output_directory, 'SI.tif')
    with rio.open(outpath, 'w', **profile) as dst:
        dst.write(SI, 1)

    return SI



# raster_file_lists = create_file_lists(months, years)
# get_monthly_averages(raster_file_lists)
# get_annual_average()
SI = calc_seasonality_index()


# # Open raster and plot
raster_path = os.path.join(output_directory, 'SI.tif')
with rio.open(raster_path) as src:
    raster_data = src.read(1)  # Read the first band
    raster_meta = src.meta
    omit_value = 0
    masked_data = np.where(raster_data == omit_value, np.nan, raster_data)
fig, ax = plt.subplots()
show(masked_data, transform=raster_meta['transform'], ax=ax, cmap='viridis') # You can change the cmap
ax.set_title('Seasonality Index')
plt.show()
