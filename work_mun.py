import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
import os

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')


parser.add_argument('--path_to_shp',   type=str, default="./data/Tmin___Tmax_data/Clase_Urbano_All.shp", help='path to the shapefile')
parser.add_argument('--cod_mun',      type=int, default=11001, help='code of the municipio to download raster data')
parser.add_argument('--path_to_save', type=str, default='results/df_results.csv', help='code of the municipio to download raster data')

args = parser.parse_args()


shp_path = args.path_to_shp

df_urbano = gpd.read_file(shp_path)
cod_mun_list = df_urbano["COD_MUN"].unique()

url_path = 'http://data.chc.ucsb.edu/products/CHIRTSdaily/v1.0/global_tifs_p05'
dates_download = pd.date_range(start='1983', end='2017', freq='1d')


if not os.path.exists('temp'):
    os.mkdir('temp')

from shapely.ops import cascaded_union
from shapely.geometry import mapping
from rasterio.mask import mask
import itertools

df_urbano["COD_MUN"] = df_urbano["COD_MUN"].map(lambda x: int(x))
cod_muns = df_urbano["COD_MUN"].unique()

df_response = pd.DataFrame(columns=["date", "code_muns", "tmax_mean", "tmax_median", "tmax_std",
                                                        "tmin_mean", "tmin_median", "tmin_std"])
df_response["date"]      = list(dates_download)
df_response["code_muns"] = args.cod_mun

df_response = df_response.set_index(["date", "code_muns"])

from tqdm import tqdm
for date in tqdm(dates_download):
    try:
        url_tmax =  os.path.join(url_path, 'Tmax', date.strftime('%Y'), 'Tmax.{}.{}.{}.tif'.format(date.strftime('%Y'), date.strftime('%m').zfill(1), date.strftime('%d').zfill(1) ) )
        url_tmin =  os.path.join(url_path, 'Tmin', date.strftime('%Y'), 'Tmin.{}.{}.{}.tif'.format(date.strftime('%Y'), date.strftime('%m').zfill(1), date.strftime('%d').zfill(1) ) )

        temp_tmax = rasterio.open(url_tmax)
        temp_tmin = rasterio.open(url_tmin)

        cm = args.cod_mun

        df_urbano_mun = df_urbano[df_urbano["COD_MUN"]==cm]
        df_urbano_mun = gpd.GeoSeries(cascaded_union(df_urbano_mun["geometry"]))

        tmax_array, _ = mask(temp_tmax, [mapping(df_urbano_mun.iloc[-1].geometry)], crop=True)
        tmin_array, _ = mask(temp_tmin, [mapping(df_urbano_mun.iloc[-1].geometry)], crop=True)

        df_response.loc[date, int(cm)]["tmax_mean"]   = tmax_array.mean()
        df_response.loc[date, int(cm)]["tmax_median"] = np.median(tmax_array)
        df_response.loc[date, int(cm)]["tmax_std"]    = np.std(tmax_array)

        df_response.loc[date, int(cm)]["tmin_mean"]   = tmin_array.mean()
        df_response.loc[date, int(cm)]["tmin_median"] = np.median(tmin_array)
        df_response.loc[date, int(cm)]["tmin_std"]    = np.std(tmin_array)
    except:
        print("Error")

df_response.to_csv(args.path_to_save)
