# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'


import sys

from nemoa.core import log, ui

class gene:

    robjects = None
    default = 'entrezid'

    def __init__(self):

        stdout = sys.stdout

        try:
            sys.stdout = NullDevice()
            import rpy2.robjects
            self.robjects = rpy2.robjects
            sys.stdout = stdout
        except Exception as err:
            sys.stdout = stdout
            raise ImportError(
                "could not import python package 'rpy2'") from err

    def _exec_rcmd(self, rcmd = None):
        if not rcmd: return True

        log.debug('passing command to R: %s' % rcmd)
        sysstout = sys.stdout
        try:
            sys.stdout = NullDevice()
            self.robjects.r(rcmd)
            sys.stdout = sysstout
        except Exception as err:
            sys.stdout = sysstout
            raise RuntimeError("""could not execute
                R command '%s' (see logfile)""" % rcmd) from err

        return True

    def _exec_cmdlist(self, cmdlist = []):
        for rcmd in cmdlist:
            if not self._exec_rcmd(rcmd): return False
        return True

    def _load_pkg(self, pkg='org.Hs.eg.db'):
        if not self._exec_rcmd("library('%s')" % pkg) and not (
            self._install_pkg(pkg) and
            self._exec_rcmd("library('%s')" % pkg)): return False
        return True

    def _install_pkg(self, pkg=None):
        if not pkg:
            ui.info("trying to install bioconductor base")
        else:
            ui.info("trying to install "
                f"bioconductor package: '{pkg}'")

        # try to evaluate the remote R script biocLite()
        bioclite = "https://bioconductor.org/biocLite.R"
        sysstout = sys.stdout
        try:
            sys.stdout = NullDevice()
            from rpy2.robjects.packages import importr
            base = importr('base')
            base.source(bioclite)
            base.require('biocLite')
            sys.stdout = sysstout
        except Exception as err:
            sys.stdout = sysstout
            raise ValueError(
                f"could not evaluate remote R script: '{bioclite}'") from err

        # try to install bioconductor packages with biocLite()
        if not pkg:
            return self._exec_rcmd("biocLite()")
        return self._exec_rcmd("biocLite('%s')" % pkg)

    def convert_list(self, inlist, infmt, outfmt, filter = False,
        unique = True):
        """Return list with converted gene labels using R/bioconductor"""

        if not outfmt or outfmt == 'default': outfmt = self.default
        if infmt == outfmt: return inlist, []
        if not self.robjects:
            raise ImportError("""could not convert gene labels:
                python package 'rpy2' is not installed!""")

        # make local copy of list
        inlist = list(inlist)[:]

        # convert using various AnnotationDBI packages from Bioconductor
        if infmt in [
            'hgu95a', 'hgu95av2', 'hgu95b', 'hgu95c', 'hgu95d',
            'hgu95e', 'hgu133a', 'hgu133a2', 'hgu133b', 'hgu133plus2',
            'hthgu133a', 'hgug4100a', 'hgug4101a', 'hgug4110b',
            'hgug4111a', 'hgug4112a', 'hguqiagenv3' ]:

            # load package
            if not self._load_pkg(infmt + '.db'):
                return inlist, list(range(len(inlist)))

            # get listvector
            if not self._exec_cmdlist([
                "x <- %s%s" % (infmt, outfmt.upper()),
                "mapped_genes <- mappedkeys(x)",
                "listmap <- as.list(x[mapped_genes])" ]):
                return inlist, list(range(len(inlist)))

            # strip leading 'X' for column select
            slist = [a.lstrip('X') for a in inlist]

        elif infmt == 'entrezid':

            # load bioconductor annotation package
            if not self._load_pkg('org.Hs.eg.db'):
                return inlist, list(range(len(inlist)))

            # get listvector
            if not self._exec_cmdlist([
                "x <- org.Hs.eg%s" % (outfmt.upper()),
                "mapped_genes <- mappedkeys(x)",
                "listmap <- as.list(x[mapped_genes])" ]):
                return inlist, list(range(len(inlist)))

            # pass list for column select
            slist = inlist

        elif outfmt == 'entrezid':

            # load bioconductor annotation package
            if not self._load_pkg('org.Hs.eg.db'):
                return inlist, list(range(len(inlist)))

            # get listvector
            if not self._exec_cmdlist([
                "x <- org.Hs.eg%s2EG" % (infmt.upper()),
                "mapped_genes <- mappedkeys(x)",
                "listmap <- as.list(x[mapped_genes])" ]):
                return inlist, list(range(len(inlist)))

            # pass list for column select
            slist = inlist

        else:
            raise ValueError("""conversion from '%s' to '%s' is not
                supported""" % (infmt, outfmt))

        # search listvector
        blist = []
        log.debug("""passing command to R (per column):
            sym <- listmap['COLUMNNAME']; sym <- unlist(sym)""")
        sysstout = sys.stdout
        sys.stdout = NullDevice()
        for id, label in enumerate(slist):
            label = label.strip(' ,\n\t\"')
            self.robjects.r("sym <- listmap['%s']" % (label))
            rselect = self.robjects.r("sym <- unlist(sym)")
            if not hasattr(rselect, '__getitem__'):
                blist.append(id)
            elif unique and rselect[0] in inlist[:id-1]:
                blist.append(id)
                n = 2
                while "%s-%i" % (rselect[0], n) in inlist[:id-1]: n += 1
                inlist[id] = "%s-%i" % (rselect[0], n)
            else:
                inlist[id] = rselect[0]
        sys.stdout = sysstout

        # filter results
        if filter:
            inlist = [item for item in inlist
                if inlist.index(item) not in blist]

        return inlist, blist

class NullDevice():
    def write(self, s):
        pass
    def flush(self, s):
        pass
