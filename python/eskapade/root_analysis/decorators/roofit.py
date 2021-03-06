# ********************************************************************************
# * Project: Eskapade - A Python-based package for data analysis                 *
# * Module: root_analysis.decorators.roofit                                      *
# * Created: 2017/04/24                                                          *
# * Description:                                                                 *
# *     Decorators for PyROOT RooFit objects                                     *
# *                                                                              *
# * Authors:                                                                     *
# *     KPMG Big Data team, Amstelveen, The Netherlands                          *
# *                                                                              *
# * Redistribution and use in source and binary forms, with or without           *
# * modification, are permitted according to the terms listed in the file        *
# * LICENSE.                                                                     *
# ********************************************************************************

import ROOT
from ROOT import RooFit


def coll_iter(coll):
    """Iterate over items in RooAbsCollection"""

    it = coll.fwdIterator()
    obj = it.next()
    while obj:
        yield obj
        obj = it.next()


def ws_contains(ws, key):
    """Check if RooWorkspace contains an object"""

    if isinstance(key, str):
        return bool(ws.obj(key))
    try:
        obj = ws.obj(key if isinstance(key, str) else key.GetName())
        return obj == key
    except:
        return False


def ws_put(ws, *args):
    """Put object in RooWorkspace"""

    ws_import = getattr(ROOT.RooWorkspace, 'import')
    if len(args) == 1 and any(isinstance(args[0], c) for c in (ROOT.RooAbsArg, ROOT.RooArgSet, ROOT.RooAbsData)):
        args = args + (ROOT.RooCmdArg(),)
    return ws_import(ws, *args)


def data_set_iter(self):
    """Iterate over events in RooDataSet"""

    for it in range(self.numEntries()):
        yield self.get(it)


# set decorators
ROOT.RooAbsReal.__float__ = lambda self: self.getVal()

ROOT.RooAbsCollection.__iter__ = coll_iter
ROOT.RooAbsCollection.__getitem__ = lambda c, i: c.find(i)
ROOT.RooAbsCollection.__contains__ = lambda c, i: True if c.find(i) else False

ROOT.RooArgSet.__getitem__ = ROOT.RooAbsCollection.__getitem__
ROOT.RooArgList.__getitem__ = lambda l, i: l.at(i) if isinstance(i, int) else ROOT.RooAbsCollection.__getitem__(l, i)

ROOT.RooWorkspace.__contains__ = ws_contains
ROOT.RooWorkspace.__getitem__ = lambda ws, k: ws.obj(k)
ROOT.RooWorkspace.__setitem__ = lambda ws, k, v: getattr(ws, 'import')(v, RooFit.RenameVariable(v.GetName(), k))
ROOT.RooWorkspace.put = ws_put

ROOT.RooDataSet.__iter__ = data_set_iter

# flag functions that create objects that should be deleted
for func in [ROOT.RooAbsPdf.generate, ROOT.RooAbsPdf.fitTo, ROOT.RooAbsData.reduce]:
    func._creates = True
