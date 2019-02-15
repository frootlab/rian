# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy as np
from flab.base import otree
from nemoa.base import array

class Evaluation:

    _config = None
    _default = {
        'algorithm': 'accuracy'}
    _buffer = {}

    def __init__(self, model = None, *args, **kwds):
        """Configure evaluation to given nemoa model instance."""

        if model: self._set_model(model)

    def get(self, key, *args, **kwds):
        """ """

        # algorithms
        if key == 'algorithm':
            return self._get_algorithm(*args, **kwds)
        if key == 'algorithms':
            return self._get_algorithms(attribute='about', *args, **kwds)

        if key == 'data':
            return self._get_data(*args, **kwds)
        if key == 'model':
            return self._get_model()

        if key in self._buffer:
            return self._buffer[key]

        return False

    def _get_algorithms(self, category=None, attribute=None):
        """Get evaluation algorithms."""

        if 'algorithms' not in self._buffer:
            self._buffer['algorithms'] = {}
        algorithms = self._buffer['algorithms'].get(attribute, None)
        if not algorithms:
            algorithms = otree.get_methods(
                self, key='name', val=attribute, groupby='category')
            self._buffer['algorithms'][attribute] = algorithms
        if category:
            if category not in algorithms:
                return {}
            algorithms = algorithms[category]

        return algorithms

    def _get_algorithm(self, name, *args, **kwds):
        """Get evaluation algorithm."""
        return self._get_algorithms(*args, **kwds).get(name, None)

    def _get_data(self):
        """Get data for evaluation.

        Returns:
            Tuple of numpy arrays containing evaluation data or None
            if evaluation data could not be retrieved from dataset.

        """

        data = self._buffer.get('data', None)

        # get evaluation data from dataset
        if not data:
            system = self.model.system
            dataset = self.model.dataset
            mapping = system._get_mapping()
            cols = (mapping[0], mapping[-1])
            data = dataset.get('data', cols=cols)
            if data:
                self._buffer['data'] = data

        return data or None

    def _get_model(self):
        """Get model instance."""
        return self._buffer.get('model', None)

    def _get_compatibility(self, model):
        """Get compatibility of transformation to given model instance.

        Args:
            model: nemoa model instance

        Returns:
            True if transformation is compatible with given model, else False.

        """

        # test type of model instance and subclasses
        if not otree.has_base(model, 'Model'):
            return False
        if not otree.has_base(model.dataset, 'Dataset'):
            return False
        if not otree.has_base(model.network, 'Network'):
            return False
        if not otree.has_base(model.system, 'System'):
            return False

        # check dataset
        if (not 'check_dataset' in model.system._default['init']
            or model.system._default['init']['check_dataset'] == True) \
            and not model.system._check_dataset(model.dataset):
            return False

        return True

    def evaluate(self, key=None, *args, **kwds):
        """Evaluate model."""

        if key == 'dataset':
            return self.model.dataset.evaluate(*args, **kwds)
        if key == 'network':
            return self.model.network.evaluate(*args, **kwds)

        if key in ['units', 'links', 'relation']:
            category = key
            args = list(args)
            algname = kwds.pop('algorithm', args.pop(0) if args else None)
            args = tuple(args)
        else:
            algname = key
            args = list(args)
            category = kwds.pop('category', args.pop(0) if args else None)
            args = tuple(args)

        if not category:
            category = 'model'
        if not algname:
            algname = {
                'model': 'accuracy', 'units': 'accuracy', 'links': 'energy',
                'relation': 'correlation'
            }.get(category, None)

        algorithm = self._get_algorithm(algname, category=category)

        if not algorithm:
            raise Warning(
                f"could not evaluate {category}: "
                f"invalid algorithm {algname}.")

        data = kwds.pop('data', self._get_data())

        getmapping = self.model.system._get_mapping
        getunits = self.model.system._get_units

        # prepare non keyword arguments for evaluation
        args = {
            'none': [], 'input': [data[0]], 'output': [data[1]],
            'all': [data]
        }.get(algorithm.get('args', None), [data])

        # get category specific keyword arguments
        if category == 'relation':
            transform = kwds.pop('transform', '')
            rettype = kwds.pop('format', 'dict')
            evalstat = kwds.pop('evalstat', True)
        elif category in ['units', 'links'] \
            and kwds.get('units', None):
            kwds['mapping'] = \
                getmapping(tgt=kwds.pop('units'))
        if kwds.get('mapping', None) is not None:
            kwds['mapping'] = getmapping()

        # run evaluation
        retval = algorithm['reference'](*args, **kwds)

        # format result
        retfmt = algorithm.get('retfmt', 'scalar')
        if category == 'model':
            return retval
        if category == 'units':
            if retfmt == 'vector':
                units = getunits(layer=kwds['mapping'][-1])
                return {unit: retval[:, uid] \
                    for uid, unit in enumerate(units)}
            if retfmt == 'scalar':
                units = getunits(layer=kwds['mapping'][-1])
                return dict(list(zip(units, retval)))
        elif category == 'links':
            if retfmt == 'scalar':
                from nemoa.math import matrix
                src = getunits(layer=kwds['mapping'][0])
                tgt = getunits(layer=kwds['mapping'][-1])
                return array.as_dict(retval, labels=(src, tgt))
        elif category == 'relation':
            if algorithm['retfmt'] == 'scalar':

                # (optional) transform relation using 'transform' string
                if transform:
                    M = retval
                    # 2do: calc real relation
                    if 'C' in transform:
                        C = self.model.system._get_unitcorrelation(data)
                    try:
                        T = eval(transform)
                        retval = T
                    except Exception as err:
                        raise ValueError(
                            "could not transform relations: "
                            "invalid syntax") from err

                # create formated return values
                if rettype == 'array':
                    return retval
                if rettype == 'dict':
                    from nemoa.math import matrix
                    src = getunits(layer=kwds['mapping'][0])
                    tgt = getunits(layer=kwds['mapping'][-1])
                    retval = array.as_dict(retval, labels=(src, tgt))
                    if not evalstat:
                        return retval

                    # (optional) add statistics
                    filtered = []
                    for src, tgt in retval:
                        sunit = src.split(':')[1] if ':' in src else src
                        tunit = tgt.split(':')[1] if ':' in tgt else tgt
                        if sunit == tunit:
                            continue
                        filtered.append(retval[(src, tgt)])
                    arr = np.array(filtered)
                    retval['max'] = np.amax(arr)
                    retval['min'] = np.amin(arr)
                    retval['mean'] = np.mean(arr)
                    retval['std'] = np.std(arr)
                    return retval

        raise Warning(
            "could not evaluate system units: "
            "unknown return format '%s'." % retfmt)

    def set(self, key, *args, **kwds):
        """ """

        if key == 'model':
            return self._set_model(*args, **kwds)
        if key == 'config':
            return self._set_config(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_config(self, config=None, **kwds):
        """Set evaluation configuration from dictionary."""
        self._config = {**self._default, **(config or {}), **kwds}
        return True

    def _set_model(self, model):
        """Set model."""

        if not self._get_compatibility(model):
            raise Warning("""Could not initialize
                evluation of model: evaluation is not compatible to
                model.""") or None

        # update time and config
        self.model = model

        # initialize data for evaluation
        self._get_data()

        return True
