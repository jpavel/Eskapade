# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Macro  : esk406_simulation_based_on_unbinned_data                              *
# * Created: 2017/04/06                                                            *
# *                                                                                *
# * Authors:                                                                       *
# *      KPMG Big Data team, Amstelveen, The Netherlands                           *
# *                                                                                *
# * Description:
# *
# * Imagine the situation where you wish to simulate an existing dataset consisting
# * of continuous (float) observables only, where you want the simulated dataset
# * to have the same features and characteristics as the input dataset, including
# * the all correlations between observables.
# *
# * This macro shows how this simulation can be done with roofit, by building a
# * smooth pdf of the input dataset with kernel estimatation techniques, the so-called 
# * KEYS pdf, which describes the input observables and their correlations.
# * The technique works very well to describe 1 and 2 dimensional distributions,
# * but is very cpu intensive and becomes ever more slow for higher number of dimensions.
# *
# * This macro has two settings, controlled with settings['high_num_dims'].
# * When false, the keys pdf contains 2 continuous observables. When true,
# * the keys pdf 3 dimensional. 
# *
# * Licence:
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************

import logging
log = logging.getLogger('macro.esk406_simulation_based_on_unbinned_data')

from eskapade import ConfigObject, ProcessManager
from eskapade import core_ops, analysis, visualization, root_analysis

log.debug('Now parsing configuration file esk406_simulation_based_on_unbinned_data')

#########################################################################################
# --- minimal analysis information

proc_mgr = ProcessManager()

settings = proc_mgr.service(ConfigObject)
settings['analysisName'] = 'esk406_simulation_based_on_unbinned_data'
settings['version'] = 0

#########################################################################################
# --- Analysis values, settings, helper functions, configuration flags.

settings['read_data'] = True
settings['generate'] = True
settings['make_plot'] = True
settings['high_num_dims'] = False

input_files = [os.environ['ESKAPADE'] + '/data/correlated_data.sv.gz']

#########################################################################################
# --- now set up the chains and links based on configuration flags

if settings['read_data']:
    ch = proc_mgr.add_chain('Data')

    # --- 0. read the input dataset
    readdata = analysis.ReadToDf(name='reader', key='correlated_data', reader='csv', sep=' ')
    readdata.path = input_files
    ch.add_link(readdata)

    # --- 1. convert into a roofit dataset (roodataset)
    #        build a KEYS pdf out of the dataset as well
    df2rds = root_analysis.ConvertDataFrame2RooDataSet()
    df2rds.read_key = readdata.key
    df2rds.store_key = 'rds_' + readdata.key
    df2rds.store_key_vars = 'keys_varset'
    df2rds.columns = ['x2', 'x3', 'x4'] if settings['high_num_dims'] else ['x2', 'x3']
    df2rds.store_index = False
    # build a KEYS pdf out of the roodataset, used for simulation below
    df2rds.create_keys_pdf = 'keys_Ndim'
    ch.add_link(df2rds)

    pds = core_ops.PrintDs(name='pds1')
    ch.add_link(pds)

if settings['generate']:
    # --- 2. simulate a new dataset with the keys pdf, and then plot this dataset
    ch = proc_mgr.add_chain('WsOps')
    wsu = root_analysis.WsUtils()
    wsu.add_simulate(pdf='keys_Ndim', obs='keys_varset', num=5000, key='simdata', into_ws=True)
    wsu.add_plot(obs='x2', data='simdata', file='x2_simdata.pdf')
    wsu.add_plot(obs='x3', data='simdata', file='x3_simdata.pdf')
    if settings['high_num_dims']:
        wsu.add_plot(obs='x4', data='simdata', file='x4_simdata.pdf')
    wsu.copy_into_ds = ['simdata']
    ch.add_link(wsu)

    # clear all from ds
    dl = core_ops.DsObjectDeleter()
    dl.deletionKeys = ['keys_Ndim']
    ch.add_link(dl)

if settings['make_plot']:
    # --- 3. make a summary report out of the simulated dataset
    ch = proc_mgr.add_chain('Plotting')

    rds2df = root_analysis.ConvertRooDataSet2DataFrame()
    rds2df.read_key = 'simdata'
    rds2df.store_key = 'df_simdata'
    ch.add_link(rds2df)

    hf = root_analysis.RootHistFiller()
    hf.columns = ['x2', 'x3', 'x4', ['x2', 'x3'], ['x3', 'x4'], ['x2', 'x4']] if settings['high_num_dims'] else ['x2', 'x3', ['x2', 'x3']]
    hf.read_key = 'df_simdata'
    hf.store_key = 'hist'
    hf.var_min_value = {'x2': -5, 'x3': -5, 'x4': -5}
    hf.var_max_value = {'x2': 5, 'x3': 5, 'x4': 5}
    ch.add_link(hf)

    # --- make a nice summary report of the created histograms
    hs = visualization.HistSummary(name='HistogramSummary', read_key=hf.store_key)
    ch.add_link(hs)

    pds = core_ops.PrintDs()
    ch.add_link(pds)

    

#########################################################################################

log.debug('Done parsing configuration file esk406_simulation_based_on_unbinned_data')
