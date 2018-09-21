# built-in python modules
import datetime
import inspect
import os

# scientific python add-ons
import numpy as np
import pandas as pd

# # plotting stuff
# # first line makes the plots appear in the notebook
# import matplotlib
#
# # https://stackoverflow.com/questions/37604289/tkinter-tclerror-no-display-name-and-no-display-environment-variable/37605654#37605654
# matplotlib.use('Agg')
#
# import matplotlib.pyplot as plt
# import matplotlib as mpl

# finally, we import the pvlib library
from pvlib import solarposition,irradiance,atmosphere,pvsystem
from pvlib.forecast import GFS, NAM, NDFD, RAP, HRRR



# Choose a location.
# Tucson, AZ
latitude = 32.2
longitude = -110.9
tz = 'US/Mountain'

surface_tilt = 30
surface_azimuth = 180 # pvlib uses 0=North, 90=East, 180=South, 270=West convention
albedo = 0.2



start = pd.Timestamp(datetime.date.today(), tz=tz) # today's date
end = start + pd.Timedelta(days=7) # 7 days from today



# Define forecast model
fm = GFS()
#fm = NAM()
#fm = NDFD()
#fm = RAP()
#fm = HRRR()



# Retrieve data
forecast_data = fm.get_processed_data(latitude, longitude, start, end)
ghi = forecast_data['ghi']

sandia_modules = pvsystem.retrieve_sam('SandiaMod')
sandia_module = sandia_modules.Canadian_Solar_CS5P_220M___2009_



# retrieve time and location parameters
time = forecast_data.index
a_point = fm.location

solpos = a_point.get_solarposition(time)
dni_extra = irradiance.get_extra_radiation(fm.time)
airmass = atmosphere.get_relative_airmass(solpos['apparent_zenith'])
poa_sky_diffuse = irradiance.haydavies(surface_tilt, surface_azimuth,
                           forecast_data['dhi'], forecast_data['dni'], dni_extra,
                           solpos['apparent_zenith'], solpos['azimuth'])

poa_ground_diffuse = irradiance.get_ground_diffuse(surface_tilt, ghi, albedo=albedo)
aoi = irradiance.aoi(surface_tilt, surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'])

poa_irrad = irradiance.poa_components(aoi, forecast_data['dni'], poa_sky_diffuse,
                                        poa_ground_diffuse)

temperature = forecast_data['temp_air']
wnd_spd = forecast_data['wind_speed']
pvtemps = pvsystem.sapm_celltemp(poa_irrad['poa_global'], wnd_spd, temperature)

effective_irradiance = pvsystem.sapm_effective_irradiance(poa_irrad.poa_direct,
                            poa_irrad.poa_diffuse, airmass, aoi, sandia_module)
sapm_out = pvsystem.sapm(effective_irradiance, pvtemps['temp_cell'], sandia_module)
# print(sapm_out.head())
print(sapm_out['p_mp'])
plot = "pop"
# sapm_out[['p_mp']].plot()
# plt.ylabel('DC Power (W)')
# plot = plt.savefig('tmp.png')

# sapm_inverters = pvsystem.retrieve_sam('sandiainverter')
# sapm_inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
# p_ac = pvsystem.snlinverter(sapm_out.v_mp, sapm_out.p_mp, sapm_inverter)
#
# p_ac.plot()
# plt.ylabel('AC Power (W)')
# plt.ylim(0, None)
