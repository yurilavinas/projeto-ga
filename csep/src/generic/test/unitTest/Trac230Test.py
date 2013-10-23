"""
Module Trac230Test
"""

__version__ = "$Revision$"
__revision__ = "$Id$"


import sys, os, unittest, shutil, datetime, glob

import CSEPFile, CSEPInitFile

from CSEPTestCase import CSEPTestCase
from EvaluationTest import EvaluationTest
from OneDayModelPostProcess import OneDayModelPostProcess
from RELMCatalog import RELMCatalog
from RELMTest import RELMTest
from RELMNumberTest import RELMNumberTest, Delta1, Delta2
from ForecastGroup import ForecastGroup
from CSEPLogging import CSEPLogging


# Logger object for the module
__logger = None


#-------------------------------------------------------------------------------
# Function to access logger object for the module.
#-------------------------------------------------------------------------------
def _moduleLogger():
    """ Get logger object for the module, initialize one if it does not exist"""
    
    global __logger
    if __logger is None:
        __logger = CSEPLogging.getLogger(__name__)
    
    return __logger


#------------------------------------------------------------------------------
#
# Test a fix for Trac ticket #230: Row-order iteration is used on 
# column-order cell array of modification catalogs generated in Python 
#
class Trac230Test (CSEPTestCase):

    # Directory with reference data for the tests
    __referenceDir = os.path.join(CSEPTestCase.ReferenceDataDir, 
                                  'unitTest',
                                  'tracTicket230')

    # Static data of the class
    
    # XML element variables to evaluate in test results
    __evaluateXMLVars = [Delta1, 
                         Delta2,
                         RELMTest.Result.ModificationCount,
                         RELMTest.Result.Modification,
                         RELMNumberTest.Result.EventCount,
                         RELMNumberTest.Result.EventCountForecast,
                         RELMNumberTest.Result.CDFEventCount,
                         RELMNumberTest.Result.CDFCount,
                         RELMNumberTest.Result.CDFValues]
    

    #---------------------------------------------------------------------------
    #
    # Run N-Test evaluation test for one-day forecast using modified catalogs
    # generated by Matlab code, and verify that all modified catalogs were used
    # by the evaluation test.
    #
    def testMatlabModificationCatalogs(self):
        """ Run N-test evaluation test with Matlab generated catalogs with \
applied uncertainties and succeed."""

        # Setup test name
        CSEPTestCase.setTestName(self, 
                                 self.id())
        
        # Directories with forecast and catalog files
        forecast_dir = 'matlabGenerated/forecasts'
        catalog_dir = 'matlabGenerated/catalog'
        reference_dir = 'matlabGenerated/referenceData'
        
        self.__evaluationTest(forecast_dir,
                              catalog_dir,
                              reference_dir,
                              datetime.datetime(2010, 4, 25))
        

    #---------------------------------------------------------------------------
    #
    # Run N-Test evaluation test for one-day forecast using modified catalogs
    # generated by Python code, and verify that all modified catalogs were used
    # by the evaluation test.
    #
    def testPythonModificationCatalogs(self):
        """ Run N-test evaluation test with Python generated catalogs with \
applied uncertainties and succeed."""

        # Setup test name
        CSEPTestCase.setTestName(self, 
                                 self.id())
        
        # Directories with forecast and catalog files
        forecast_dir = 'pythonGenerated/forecasts'
        catalog_dir = 'pythonGenerated/catalog'
        reference_dir = 'pythonGenerated/referenceData'
        
        self.__evaluationTest(forecast_dir,
                              catalog_dir,
                              reference_dir,
                              datetime.datetime(2010, 6, 20))
        

    #---------------------------------------------------------------------------
    #
    # Run evaluation test for the forecast, and validate the results.
    #
    # Inputs:
    #            forecast_dir - Directory that stores forecast files for 
    #                           evaluation.
    #            catalog_dir - Directory that stores catalog files for
    #                          evaluation.
    #            reference_dir - Directory with reference result data to validate
    #                            generated test results with.
    #            test_date - Test date for evaluation
    #            
    #
    def __evaluationTest(self, 
                         forecast_dir,
                         catalog_dir,
                         reference_dir,
                         test_date):
        """ Run evaluation test for the forecast using provided catalog files
            and succeed."""


        ### Generate test directory
        RELMCatalog(CSEPTestCase.TestDirPath)

        __test_forecast_dir = os.path.join(CSEPTestCase.TestDirPath, 
                                           os.path.basename(forecast_dir))
        
        shutil.copytree(os.path.join(Trac230Test.__referenceDir, 
                                     forecast_dir),
                        __test_forecast_dir)   

        __test_catalog_dir = os.path.join(CSEPTestCase.TestDirPath, 
                                          os.path.basename(catalog_dir))
        shutil.copytree(os.path.join(Trac230Test.__referenceDir, 
                                     catalog_dir),
                        __test_catalog_dir)   

        # ForecastGroup object that represents forecast models for the test
        forecast_group = ForecastGroup(__test_forecast_dir,
                                       OneDayModelPostProcess.Type,
                                       RELMNumberTest.Type)

        # Use the same directory for catalog data and test results
        for each_test in forecast_group.tests:
           each_test.run(test_date, 
                         __test_catalog_dir,
                         __test_catalog_dir)

        
        ### Evaluate test results
        reference_file = glob.glob('%s/*xml' %os.path.join(Trac230Test.__referenceDir,
                                                           reference_dir))[0]
        test_file = os.path.join(CSEPTestCase.TestDirPath,
                                 __test_catalog_dir,
                                 os.path.basename(reference_file))
        
        _moduleLogger().info("Comparing reference evaluation \
test file %s with generated evaluation test file %s..." %(reference_file, 
                                                          test_file)) 

        # If result filename in XML format, extract variables names  to evaluate
        diff_precision = 5E-5 
        for each_test in forecast_group.tests:
            
            # Open reference file
            ref_obj = CSEPInitFile.CSEPInitFile(reference_file)
            
            # Open test result file
            test_obj = CSEPInitFile.CSEPInitFile(test_file)
            
            # Evaluate variables specific to the test
            for each_var in Trac230Test.__evaluateXMLVars:
                
                # There might be multiple elements with the same tag name:
                # validation relies on the fact that reference and generated
                # result data will have the corresponding elements listed in the
                # same order
                num_var_elements = ref_obj.elements(each_var)
                for var_index in xrange(len(num_var_elements)):
                     
                    # Reference data was generated by Matlab and written with at 
                    # most 8 digits of precision
                    ref_data = ref_obj.elementValue(each_var,
                                                    index = var_index)
                    
                    # Round up test data to be compatible with at most 8 digits
                    # of precision for reference data
                    test_data = test_obj.elementValue(each_var,
                                                      index = var_index)
                    
                    _moduleLogger().info(\
"Comparing reference var %s: %s vs. %s" %(each_var, ref_data, test_data)) 

                    self.failIf(CSEPFile.compareLines(ref_data, 
                                                      test_data,
                                                      diff_precision) is False,
                                "Failed to compare evaluation test results for %s: expected %s, got %s"
                                %(each_var, 
                                  ref_data,
                                  test_data))


# Invoke the module
if __name__ == '__main__':
   
   # Invoke all tests
   unittest.main()
        
# end of main
