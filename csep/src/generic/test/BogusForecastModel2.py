"""
Module BogusForecastModel2
"""

__version__ = "$Revision$"
__revision__ = "$Id$"


import sys, os, datetime, string
import numpy as np

import Environment, CSEPFile
from OneDayForecast import OneDayForecast
from Forecast import Forecast


#--------------------------------------------------------------------------------
#
# BogusForecastModel2 forecast model.
#
# This class is designed to test CSEP functionality of properly handling forecast
# models in the running system.
#
class BogusForecastModel2 (OneDayForecast):

    # Static data of the class
    
    # Keyword identifying type of the class
    Type = "BogusForecastModel2"

    # Flag if input catalog is required to generate forecast
    RequireInputCatalog = True
    

    #--------------------------------------------------------------------
    #
    # Initialization.
    #
    # Input: 
    #        dir_path - Directory to store forecast file to.
    #        args - Optional arguments for the model. Default is None.    
    # 
    def __init__ (self, dir_path, args = None):
        """ Initialization for BogusForecastModel2 class"""
        
        OneDayForecast.__init__(self, dir_path)

        self.__data = None
       

    #--------------------------------------------------------------------
    #
    # Set data for the forecast.
    #
    # Input: numpy array object to set data to
    #
    # Output: None
    #
    def data (self,
              np_data):
        """ Sets data of forecast to provided object."""
        
        self.__data = np_data


    #--------------------------------------------------------------------
    #
    # Return keyword identifying the model.
    #
    # Input: None.
    #
    # Output:
    #           String identifying the type
    #
    def type (self):
        """ Returns keyword identifying the forecast model type."""
        
        return self.Type


    #--------------------------------------------------------------------
    #
    # Write input parameter file for the model.
    #
    # Input: None
    #        
    def writeParameterFile (self):
        """ Format input parameter file for the model.
            Created file will be used by R script that invokes the
            model."""

        fhandle = Forecast.writeParameterFile(self)

        # Close the file
        fhandle.close()


    #---------------------------------------------------------------------------
    # Return flag that indicates if forecast model requires input catalog. 
    # Defauls is True meaning that forecast model requires input catalog 
    # from authorized data source.
    # 
    def requiresInputCatalog (self):
        """ Flag if forecast model requires input catalog. Default is True meaning  
            that forecast model requires input catalog from authorized data source."""
            
        return BogusForecastModel2.RequireInputCatalog


    #---------------------------------------------------------------------------
    #
    # Invoke the model (simulate forecast generation by touching the file
    #
    # Input: None
    #        
    def run (self):
        """ Run forecast: 'touch' forecast file"""
        
        if self.__data is None:
            Environment.invokeCommand('touch %s' %self.filename())
            
        else:
            # Write provided data to the file
            np.savetxt(self.filename(), 
                       self.__data)
