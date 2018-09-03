# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

from nemoa.common import classes

class Evaluation:

    _config = None
    _default = {
        'algorithm': 'accuracy'}
    _buffer = {}

    def __init__(self, model = None, *args, **kwargs):
        """Configure evaluation to given nemoa model instance."""

        if model: self._set_model(model)

    def get(self, key, *args, **kwargs):
        """ """

        # algorithms
        if key == 'algorithm':
            return self._get_algorithm(*args, **kwargs)
        if key == 'algorithms': return self._get_algorithms(
            attribute = 'about', *args, **kwargs)

        if key == 'data': return self._get_data(*args, **kwargs)
        if key == 'model': return self._get_model()

        if key in self._buffer: return self._buffer[key]

        return False

    def _get_algorithms(self, category = None, attribute = None):
        """Get evaluation algorithms."""

        from nemoa.common import classes

        if 'algorithms' not in self._buffer: self._buffer['algorithms'] = {}
        algorithms = self._buffer['algorithms'].get(attribute, None)
        if not algorithms:
            algorithms = classes.methods(self, renamekey = 'name',
                grouping = 'category', attribute = attribute)
            self._buffer['algorithms'][attribute] = algorithms
        if category:
            if category not in algorithms: return {}
            algorithms = algorithms[category]

        return algorithms

    def _get_algorithm(self, name, *args, **kwargs):
        """Get evaluation algorithm."""
        return self._get_algorithms(*args, **kwargs).get(name, None)

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
            data = dataset.get('data', cols = cols)
            if data: self._buffer['data'] = data

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
        if not classes.hasbase(model, 'model'): return False
        if not classes.hasbase(model.dataset, 'dataset'): return False
        if not classes.hasbase(model.network, 'network'): return False
        if not classes.hasbase(model.system, 'system'): return False

        # check dataset
        if (not 'check_dataset' in model.system._default['init']
            or model.system._default['init']['check_dataset'] == True) \
            and not model.system._check_dataset(model.dataset):
            return False

        return True

    def evaluate(self, key = None, *args, **kwargs):
        """Evaluate model."""

        if key == 'dataset':
            return self.model.dataset.evaluate(*args, **kwargs)
        if key == 'network':
            return self.model.network.evaluate(*args, **kwargs)

        if key in ['units', 'links', 'relation']:
            category = key
            args = list(args)
            algname = kwargs.pop('algorithm', args.pop(0) if args else None)
            args = tuple(args)
        else:
            algname = key
            args = list(args)
            category = kwargs.pop('category', args.pop(0) if args else None)
            args = tuple(args)

        if not category: category = 'model'
        if not algname: algname = {
            'model': 'accuracy',
            'units': 'accuracy',
            'links': 'energy',
            'relation': 'correlation' }.get(category, None)

        algorithm = self._get_algorithm(algname, category = category)

        if not algorithm: raise Warning(
            f"could not evaluate {category}: invalid algorithm {algname}.")

        data = kwargs.pop('data', self._get_data())

        getmapping = self.model.system._get_mapping
        getunits = self.model.system._get_units

        # prepare non keyword arguments for evaluation
        args = {'none': [], 'input': [data[0]], 'output': [data[1]],
            'all': [data]}.get(algorithm.get('args', None), [data])

        # get category specific keyword arguments
        if category == 'relation':
            transform = kwargs.pop('transform', '')
            rettype = kwargs.pop('format', 'dict')
            evalstat = kwargs.pop('evalstat', True)
        elif category in ['units', 'links'] \
            and kwargs.get('units', None):
            kwargs['mapping'] = \
                getmapping(tgt = kwargs.pop('units'))
        if kwargs.get('mapping', None) is not None:
            kwargs['mapping'] = getmapping()

        # run evaluation
        retval = algorithm['reference'](*args, **kwargs)

        # format result
        retfmt = algorithm.get('retfmt', 'scalar')
        if category == 'model':
            return retval
        elif category == 'units':
            if retfmt == 'vector':
                units = getunits(layer = kwargs['mapping'][-1])
                return {unit: retval[:, uid] \
                    for uid, unit in enumerate(units)}
            elif retfmt == 'scalar':
                units = getunits(layer = kwargs['mapping'][-1])
                return dict(list(zip(units, retval)))
        elif category == 'links':
            if retfmt == 'scalar':
                src = getunits(layer = kwargs['mapping'][0])
                tgt = getunits(layer = kwargs['mapping'][-1])
                from nemoa.common.dict import array_to_dict
                return array_to_dict(retval, (src, tgt))
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
                    except Exception as e:
                        raise ValueError("could not transform relations: "
                            "invalid syntax") from e

                # create formated return values
                if rettype == 'array': return retval
                if rettype == 'dict':
                    src = getunits(layer = kwargs['mapping'][0])
                    tgt = getunits(layer = kwargs['mapping'][-1])
                    from nemoa.common.dict import array_to_dict
                    retval = array_to_dict(retval, (src, tgt))
                    if not evalstat: return retval

                    # (optional) add statistics
                    filtered = []
                    for src, tgt in retval:
                        sunit = src.split(':')[1] if ':' in src else src
                        tunit = tgt.split(':')[1] if ':' in tgt else tgt
                        if sunit == tunit: continue
                        filtered.append(retval[(src, tgt)])
                    array = numpy.array(filtered)
                    retval['max'] = numpy.amax(array)
                    retval['min'] = numpy.amin(array)
                    retval['mean'] = numpy.mean(array)
                    retval['std'] = numpy.std(array)
                    return retval

        raise Warning(
            "could not evaluate system units: "
            "unknown return format '%s'." % retfmt)

    def set(self, key, *args, **kwargs):
        """ """

        if key == 'model': return self._set_model(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)

        raise KeyError(f"unknown key '{key}'")

    def _set_config(self, config = None, **kwargs):
        """Set evaluation configuration from dictionary."""

        from nemoa.common.dict import merge
        if not isinstance(config, dict): config = {}
        self._config = merge(kwargs, config, self._default)

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
