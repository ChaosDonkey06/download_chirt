import geopandas as gpd
import pandas as pd
import rasterio
import os


shp_path = "./data/Tmin___Tmax_data/Clase_Urbano_All.shp"

df_urbano = gpd.read_file(shp_path)
cod_mun_list = df_urbano["COD_MUN"].unique()

url_path = 'http://data.chc.ucsb.edu/products/CHIRTSdaily/v1.0/global_tifs_p05'
dates_download = pd.date_range(start='1983', end='2017', freq='1d')


all_url_tmax = [os.path.join(url_path, 'Tmax', y.strftime('%Y'), 'Tmax.{}.{}.{}.tif'.format(y.strftime('%Y'), y.strftime('%m').zfill(1), y.strftime('%d').zfill(1) ) ) for y in dates_download]
all_url_tmin = [os.path.join(url_path, 'Tmin', y.strftime('%Y'), 'Tmin.{}.{}.{}.tif'.format(y.strftime('%Y'), y.strftime('%m').zfill(1), y.strftime('%d').zfill(1) ) ) for y in dates_download]


if not os.path.exists('temp'):
    os.mkdir('temp')

one_date = all_url_tmax[0]
src = rasterio.open(one_date)

clipped_array, clipped_transform = rasterio.mask.mask(src, [mapping(df.iloc[0].geometry)], crop=True)