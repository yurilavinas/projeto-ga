"""
Module Trac232Test
"""

__version__ = "$Revision$"
__revision__ = "$Id$"


import sys, os, unittest, shutil, glob

import CSEPFile, Environment
from CSEPTestCase import CSEPTestCase
from Dispatcher import Dispatcher
from DispatcherInitFile import DispatcherInitFile
from CSEPOptions import CommandLineOptions
from CSEPInitFile import CSEPInitFile
from RELMTest import RELMTest


 #------------------------------------------------------------------------------
 #
 #
 # Validate fix for Trac ticket #232: Empty catalog passed to 
 # CSEPGeneric.Catalog.modifications() to generate catalog uncertainties raises
 # 'IndexError: index out of bounds' exception
 #
class Trac232Test (CSEPTestCase):

   # Static data of the class
   
   # Unit tests use sub-directory of global reference data directory
   __referenceDataDir = os.path.join(CSEPTestCase.ReferenceDataDir, 
                                     'unitTest', 
                                     'tracTicket232')

   
   #--------------------------------------------------------------------
   #
   # This test verifies that Dispatcher publishes result plots to the
   # specified host and directory.
   #
   def testEmptyCatalog(self):
      """ Confirm that empty catalog passed to the CSEPGeneric.Catalog.modifications()
          creates valid array of catalogs with applied uncertainties."""

      # Setup test name
      CSEPTestCase.setTestName(self, 
                               self.id())
      

      # Copy forecast group directory to the runtime test directory
      group_dir = "forecasts"
      shutil.copytree(os.path.join(Trac232Test.__referenceDataDir, 
                                   group_dir),
                      os.path.join(CSEPTestCase.TestDirPath, 
                                   group_dir))
      
      # Copy dispatcher initialization file and replace forecast group 
      # directory with runtime path - it can't be a relative
      # path to the dispatcher's directory
      xmldoc = DispatcherInitFile(os.path.join(Trac232Test.__referenceDataDir,
                                               "dispatcher.init.xml"))
      groups = xmldoc.elements(DispatcherInitFile.ForecastGroupElement)
      groups[0].text = os.path.join(CSEPTestCase.TestDirPath, group_dir)

      # Use pre-processed data from specified directory
      dirs = xmldoc.elements(DispatcherInitFile.RootDirectoryElement)
      dirs[0].attrib[DispatcherInitFile.PreProcessedDataDirAttribute] = Trac232Test.__referenceDataDir
      dirs[0].attrib[DispatcherInitFile.RawDataDirAttribute] = Trac232Test.__referenceDataDir
      
      # Write modified file to the test directory
      init_file = os.path.join(CSEPTestCase.TestDirPath, "dispatcher.init.xml")
      
      fhandle = CSEPFile.openFile(init_file, 
                                  CSEPFile.Mode.WRITE)
      xmldoc.write(fhandle)
      fhandle.close()
      
      cwd = os.getcwd() 
      os.chdir(CSEPTestCase.TestDirPath)
      
      num_modified_catalogs = 5
      
      try:
         
         # Clear exceptions generated by other unit tests
         sys.exc_clear()
         del sys.argv[1:]
         
         # Simulate command-line arguments
         option = "--year=2010"
         sys.argv.append(option)
         
         option = "--month=7"  
         sys.argv.append(option)         
         
         option = "--day=5"        
         sys.argv.append(option)         
         
         # Don't download raw data and don't pre-process
         sys.argv.append(CommandLineOptions.DOWNLOAD_RAW)
         sys.argv.append(CommandLineOptions.PREPROCESS_RAW)         
         
         # Enable forecast map generation
         sys.argv.append(CommandLineOptions.FORECAST_MAP)
         
         # Enable forecast master XML template 
         sys.argv.append(CommandLineOptions.FORECAST_TEMPLATE)
         
         option = "%s=0" %CommandLineOptions.WAITING_PERIOD
         sys.argv.append(option)
         
         option = "%s=%s" %(CommandLineOptions.NUM_CATALOG_VARIATIONS,
                            num_modified_catalogs)
         sys.argv.append(option)

         object = Dispatcher()
         object.run()
         
      finally:
         os.chdir(cwd)
            
    
      # Verify that expected number of modified catalogs are generated
      result_file_path = os.path.join(CSEPTestCase.TestDirPath,
                                      'forecasts',
                                      'results/2010-07-05/*RELMTest.rTest_N-Test_BogusForecastModel1_7_5_2010-fromXML.xml*1')
      
      result_files = glob.glob(result_file_path)
      
      self.failIf(len(result_files) != 1,
                  "Expected one result file of %s pattern, got %s" %(result_file_path,
                                                                     len(result_files)))

      result_obj = CSEPInitFile(result_files[0])
      
      count_val = int(result_obj.elementValue(RELMTest.Result.ModificationCount))
      
      self.failIf(count_val != num_modified_catalogs,
                  "Expected %s=%s, got %s" %(RELMTest.Result.ModificationCount,
                                             num_modified_catalogs,
                                             count_val))

      modifications_count = len(result_obj.elementValue(RELMTest.Result.Modification).split(' '))
      
      self.failIf(modifications_count != num_modified_catalogs,
                  "Expected %s values for %s, got %s" %(num_modified_catalogs,
                                                        RELMTest.Result.Modification,
                                                        modifications_count))


# Invoke the module
if __name__ == '__main__':
   
   # Invoke all tests
   unittest.main()
        
# end of main
