# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Macro  : esk205_concatenate_pandas_dfs                                         *
# * Created: 2017/02/23                                                            *
# * Description:                                                                   *
# *      Illustrates link that calls basic concat() of pandas dataframes            *
# *      See for more information pandas documentation:
# *                                                                                *
# *      http://pandas.pydata.org/pandas-docs/stable/merging.html
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************

import logging
log = logging.getLogger('macro.esk205_concatenate_pandas_dfs')

from eskapade import ConfigObject, ProcessManager, DataStore
from eskapade import core_ops, analysis

log.debug('Now parsing configuration file esk205_concatenate_pandas_dfs')

#########################################################################################
# --- minimal analysis information

settings = ProcessManager().service(ConfigObject)
settings['analysisName'] = 'esk205_concatenate_pandas_dfs'
settings['version'] = 0

#########################################################################################
# --- Analysis values, settings, helper functions, configuration flags.

# generate dummy dataframes and add to datastore
# these dataframes are concatenated below, during link execution.

# NB: realize that, normally, such dataframes are read or generated
# on the fly during link execution.

from pandas import DataFrame

ds = ProcessManager().service(DataStore)

ds['df1'] = DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
                       'B': ['B0', 'B1', 'B2', 'B3'],
                       'C': ['C0', 'C1', 'C2', 'C3'],
                       'D': ['D0', 'D1', 'D2', 'D3']})

ds['df2'] = DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
                       'B': ['B4', 'B5', 'B6', 'B7'],
                       'C': ['C4', 'C5', 'C6', 'C7'],
                       'D': ['D4', 'D5', 'D6', 'D7']})

ds['df3'] = DataFrame({'A': ['A8', 'A9', 'A10', 'A11'],
                       'B': ['B8', 'B9', 'B10', 'B11'],
                       'C': ['C8', 'C9', 'C10', 'C11'],
                       'D': ['D8', 'D9', 'D10', 'D11']})

#########################################################################################
# --- below we concatenate the dataframes found in the datastore

proc_mgr = ProcessManager()

ch = proc_mgr.add_chain('DataPrep')

# concatenate the three dataframes below each other during link execution
link = analysis.DfConcatenator(readKeys = ['df1', 'df2', 'df3'],
                               storeKey = 'outgoing')
# Any other kwargs given to DfConcatenator are passed on the the
# pandas concat() function.
link.set_log_level(logging.DEBUG)
ch.add_link(link)

link = core_ops.DsObjectDeleter()
link.deletionKeys = ['df1','df2','df3']
ch.add_link(link)

link = core_ops.PrintDs()
link.keys = ['n_outgoing','outgoing']
ch.add_link(link)


#########################################################################################

log.debug('Done parsing configuration file esk205_concatenate_pandas_dfs')

