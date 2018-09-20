# built-in python modules
import datetime
import inspect
import os

# scientific python add-ons
import numpy as np
import pandas as pd

# plotting stuff
# first line makes the plots appear in the notebook
# %matplotlib inline
import matplotlib.pyplot as plt
import matplotlib as mpl

# finally, we import the pvlib library
from pvlib import solarposition,irradiance,atmosphere,pvsystem
from pvlib.forecast import GFS, NAM, NDFD, RAP, HRRR

class Panel():

    def __init__(self):
        # Choose a location.
        # Tucson, AZ
        self.latitude = 32.2
        self.longitude = -110.9
        self.tz = 'US/Mountain'

        self.surface_tilt = 30
        self.surface_azimuth = 180 # pvlib uses 0=North, 90=East, 180=South, 270=West convention
        self.albedo = 0.2

#     def __init__(self, latitude, longitude, timezone, surface_tilt, surface_azimuth, albedo):
#         self.latitude = latitude
#         self.longitude = longitude
#         self.tz = timezone
#         self.surface_tilt = surface_tilt
#         self.surface_azimuth = surface_azimuth # angle (0 = North, 90 = East)
# # measure of the diffuse reflection of solar radiation out of the total solar radiation
# # https://en.wikipedia.org/wiki/Albedo
#         self.albedo = albedo

class Forecast():
    # forecast_models = [GFS(), NAM(), NDFD(), RAP(), HRRR()]

    def get_avg_daily_dc_power(self):
        total = self.sapm_out.p_mp.values.sum()
        avg = total/self.forecast_length
        return np.format_float_positional(avg, precision=3)

    def get_avg_daily_ac_power(self):
        total = self.ac_power.values.sum()
        avg = total/self.forecast_length
        return np.format_float_positional(avg, precision=3)

    # forecast_length in days
    def __init__(self, panel = None, forecast_length = 7, forecast_model = None):
        self.forecast_length = forecast_length
        if panel == None:
            self.panel = Panel()
        else:
            self.panel = panel

        if forecast_model == None:
            self.fm = GFS()
        else:
            self.fm = forecast_model

        self.start = pd.Timestamp(datetime.date.today(), tz=self.panel.tz) # today's date
        self.end = self.start + pd.Timedelta(days=forecast_length) # days from today

        # get forecast data
        forecast_data = self.fm.get_processed_data(self.panel.latitude,
                self.panel.longitude, self.start, self.end)
        ghi = forecast_data['ghi']

        # get solar position
        time = forecast_data.index
        a_point = self.fm.location
        solpos = a_point.get_solarposition(time)

        # get PV(photovoltaic device) modules
        sandia_modules = pvsystem.retrieve_sam('SandiaMod')
        sandia_module = sandia_modules.Canadian_Solar_CS5P_220M___2009_

        dni_extra = irradiance.get_extra_radiation(self.fm.time) # extra terrestrial radiation
        airmass = atmosphere.get_relative_airmass(solpos['apparent_zenith'])
        # POA: Plane Of Array: an image sensing device consisting of an array
        # (typically rectangular) of light-sensing pixels at the focal plane of a lens.
        # https://en.wikipedia.org/wiki/Staring_array

        # Diffuse sky radiation is solar radiation reaching the Earth's surface after
        # having been scattered from the direct solar beam by molecules or particulates
        # in the atmosphere.
        # https://en.wikipedia.org/wiki/Diffuse_sky_radiation
        poa_sky_diffuse = irradiance.haydavies(self.panel.surface_tilt, self.panel.surface_azimuth,
                                   forecast_data['dhi'], forecast_data['dni'], dni_extra,
                                   solpos['apparent_zenith'], solpos['azimuth'])

        # Diffuse reflection is the reflection of light or other waves or particles
        # from a surface such that a ray incident on the surface is scattered at many
        # angles rather than at just one angle as in the case of specular reflection.
        poa_ground_diffuse = irradiance.get_ground_diffuse(self.panel.surface_tilt, ghi, albedo=self.panel.albedo)

        # AOI: Angle Of Incidence
        aoi = irradiance.aoi(self.panel.surface_tilt, self.panel.surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'])

        #  irradiance is the radiant flux (power) received by a surface per unit area
        # https://en.wikipedia.org/wiki/Irradiance
        poa_irrad = irradiance.poa_components(aoi, forecast_data['dni'], poa_sky_diffuse,
                                                poa_ground_diffuse)

        temperature = forecast_data['temp_air']
        wnd_spd = forecast_data['wind_speed']

        # pvtemps: pv temperature
        pvtemps = pvsystem.sapm_celltemp(poa_irrad['poa_global'], wnd_spd, temperature)

        # irradiance actually used by PV
        effective_irradiance = pvsystem.sapm_effective_irradiance(poa_irrad.poa_direct,
                                    poa_irrad.poa_diffuse, airmass, aoi, sandia_module)

        # SAPM: Sandia PV Array Performance Model
        # https://pvpmc.sandia.gov/modeling-steps/2-dc-module-iv/point-value-models/sandia-pv-array-performance-model/

        self.sapm_out = pvsystem.sapm(effective_irradiance, pvtemps['temp_cell'], sandia_module)

        sapm_inverters = pvsystem.retrieve_sam('sandiainverter')
        sapm_inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
        self.ac_power = pvsystem.snlinverter(self.sapm_out.v_mp, self.sapm_out.p_mp, sapm_inverter)
