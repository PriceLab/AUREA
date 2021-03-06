#!/usr/bin/env python
"""
setup.py 
"""

import ez_setup
ez_setup.use_setuptools()
#from distutils.core import setup, Extension
from setuptools import setup, Extension
import os
import os.path
import shutil

def getAUREApyModules():
    """
    Returns a list of all py_modules in AUREA
    """
    #defining the modules
    GUI_mod = [ 'AUREA.GUI.'+x for x in ['App', 'Controller', 'Page', 'Results']] 
    adaptive_mod = ['AUREA.adaptive.'+x for x in ['LearnerQueue', 'ResourceEstimate']]
    packager_mod = ['AUREA.packager.'+x for x in ['DataCleaner','DataPackager']]
    parser_mod = ['AUREA.parser.' + x for x in  ['CSVParser', 'GMTParser', 'SettingsParser', 'SOFTParser', 'SynonymParser']]
    learner_mod = ["AUREA.learner.dirac", "AUREA.learner.tsp","AUREA.learner.tst", "AUREA.learner.ktsp", "AUREA.learner.wilcoxon"]
    #putting all of the python modules in oneList
    a_modules = []
    for mod_list in [GUI_mod, adaptive_mod, packager_mod, parser_mod, learner_mod]:
        for mod in mod_list:
            a_modules.append(mod)
    return a_modules

def getExtensionModuleSettings():
    """
    Returns a list of tuples with the settings for the extension modules    
    """
    ext_mod_settings = []
    ext_mod_settings.append(('AUREA.learner._dirac', ['Dirac_pywrapper.i', 'Dirac_pywrapper.cpp', 'Dirac.cpp', 'dir_Matrix.cpp','kfold.cpp' ]))
    ext_mod_settings.append(('AUREA.learner._tsp',[ 'TSP_pywrapper.i', 'TSP_pywrapper.cpp', 'learn_utsp_classifier.cpp', 'utils.cpp', 'matrix.cpp', 'wilcoxon.cpp', 'order.cpp', 'kfold.cpp' ]))
    ext_mod_settings.append(('AUREA.learner._tst',['TST_pywrapper.i', 'TST_pywrapper.cpp', 'learn_tst_classifier.cpp', 'utils.cpp', 'matrix.cpp', 'wilcoxon.cpp', 'order.cpp', 'kfold.cpp' ]))
    ext_mod_settings.append(('AUREA.learner._ktsp',['KTSP_pywrapper.i', 'KTSP_pywrapper.cpp', 'Ktsp.cpp', 'kfold.cpp',  'utils.cpp', 'matrix.cpp', 'wilcoxon.cpp', 'order.cpp']))
    ext_mod_settings.append(('AUREA.learner._wilcoxon',['WILCOXON_pywrapper.i', 'WILCOXON_pywrapper.cpp', 'wilcoxon_test.cpp', 'utils.cpp', 'matrix.cpp', 'wilcoxon.cpp', 'order.cpp' ]))
    return ext_mod_settings

def buildExtension(ext_name,src_dir, src_files, swig_opts=['-modern', '-c++']):
    """
    Builds and returns an extension module with the given settings
    """
    sources_list = [os.path.join(src_dir, src_file) for src_file in src_files]
    return Extension(ext_name, sources=sources_list, swig_opts=swig_opts)


def swig_helper( module, src_dir ):
    """
    This builds the python files that use the compiled extensions 
    (dirac.py, tst.py, etc.)
    This is already being done in build_ext, but it leaves the file
    in the src directory instead of putting it into learner where it 
    belongs, so we have to do this manually.
    """
    swig_interface = os.path.join(src_dir, module +"_pywrapper.i")
    command = 'swig -c++ -python -modern ' + swig_interface
    os.system(command)
    
    shutil.copy(os.path.join(src_dir, module.lower() + ".py"),os.sep.join(['src', 'AUREA', 'learner' ] ))

#start script

learner_modules = ["Dirac", "TSP", "TST", "KTSP", "WILCOXON"]
path_dir = ['src', 'AUREA', 'learner', 'src']
src_dir = os.sep.join(path_dir)

#copy swig generated pymodules to the learner directory
print "running swig_helper"
try:
    for mod in learner_modules:
        swig_helper(mod,src_dir)
except Exception as e:
    print "Swig Helper did not run.  This is fine if building rpms."
    #Basically if the pymodules did not get copied over you are
    #in trouble.  To get around this, try building and then running
    #bdist_rpm.
#Build extension instances
ext_mod = [ buildExtension(name, src_dir, src_files) for name, src_files in getExtensionModuleSettings()]

#run setup
from glob import glob
import sys
#sys.path.append(r'C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\redist\amd64\Microsoft.VC90.CRT')
#import py2exe
setup (name = 'AUREA',
        version='1.6.7', #edit AUREA/__init__.py
        author ='The Nathan Price Lab',
        author_email = 'john.c.earls@gmail.com',
        url= 'http://price.systemsbiology.net/AUREA/',
        description="""AUREA is a software suite that makes finding Relative Expression Learners easy.""",
        packages=['AUREA','AUREA.GUI', 'AUREA.learner', 'AUREA.packager', 'AUREA.parser','AUREA.adaptive', 'pyBabel'],
        package_dir={'AUREA': 'src/AUREA', 'pyBabel': 'src/pyBabel'},
        ext_modules = ext_mod, 
        py_modules = getAUREApyModules(),
        classifiers=[
            'License :: OSI Approved :: GNU Affero General Public License v3', 
            'Development Status :: 4 - Beta', 
            'Intended Audience :: Science/Research', 
            'Topic :: Scientific/Engineering :: Bio-Informatics', 
            'Topic :: Scientific/Engineering :: Medical Science Apps.'],
            #uncomment to use py2app
            #app=["workspace/AUREAGUI.py"],
	    
            #data_files=["workspace/data"],
            #windows=[{"script":"workspace/AUREAGUI.py", "icon_resources":[(1,"workspace/data/AUREA.ico")]}],
            #data_files=[('data',glob(r"C:\Users\earls3\AUREA\workspace\data\*")), ("Microsoft.VC90.CRT", glob(r'C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\redist\amd64\Microsoft.VC90.CRT\*')) ],
	    #zipfile="libdir\\library.zip"

)


