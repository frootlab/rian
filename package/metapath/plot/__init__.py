# -*- coding: utf-8 -*-
import metapath.common as mp

from .unitrelationgraph import *
from .samplerelationgraph import *

def new(config = {}, **kwargs):

    # return 'empty plot instance' if no configuration is given
    if config == None:
        import metapath.plot.base
        return metapath.plot.base.empty()

    # import package
    if not 'package' in config:
        mp.log("warning", "could not create plot: config is not valid")
        return None
    package = 'metapath.plot.' + config['package']
    try:
        exec "import %s" % (package)
    except:
        mp.log("warning", "could not create plot: package '%s' could not be found! (case sensitive)" % (package))
        return None

    # create class instance
    try:
        exec "plot = %s.%s(config = config)" % (package, config['class'])
        return plot
    except:
        mp.log("warning", "could not create plot: class '%s' could not be found in package '%s'!" % (config['class'], package))
        return None
