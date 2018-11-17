Glossary
========

Norms and Metrices
------------------

.. glossary::

    1-Norm
        The *1-norm* provides a length measure for the interpretation of
        vector spaces as orthogonal lattices. For a vector space of dimension
        *n*, the norm is defined by: [#taxicab]_

        .. math::
            \|\vec{x}\|_{1}
                := \sum_{i=1}^{n} |x_{i}|

        The 1-norm specifies the :term:`p-norm` for the case :math:`p=1` and
        induces the :term:`Manhattan distance` to the underlying vector space.
        When applied to a random sample, the Manhattan distance is also known as
        the :term:`sum of absolute differences`.

    Chebyshev Distance
        The *Chebyshev Distance* generates the *Chebyshev Metric*. For a
        vector space of dimension *n*, the Chebyshev distance is defined by:
        [#chebyshev]_

        .. math::
            d_{\infty}(\vec{x},\,\vec{y})
                := \underset{i}{\max}\left(|y_{i}-x_{i}|\right)

        The Chebyshev distance is induced by the :term:`Maximum norm` and
        specifies the :term:`Minkowski distance` for the transition
        :math:`p\rightarrow\infty`.

    Euclidean Distance
        The *Euclidean Distance* corresponds to the natural geometric
        interpretation of a vector space. For an underlying vector space of
        dimension *n*, the Euclidean distance is given by: [#euclid]_

        .. math::
            d_{2}(\vec{x},\,\vec{y})
                := \left(\sum_{i=1}^{n}|y_{i}-x_{i}|^{2}\right)^{1/2}

        The Euclidean distance is induced by the :term:`Euclidean norm` and
        specifies the :term:`Minkowski distance` for the case :math:`p=2`. With
        respect to regression analysis the Euclidean distance endows the
        components of a random sample with a discrepancy measure,
        between observed an estimated realizations. This discrepancy measure is
        commonly referred as :term:`Residual sum of squares` (RSS) and provides
        the foundation for the method of least squares. [#leastsquares]_

    Euclidean Norm
        The *Euclidean norm* provides the fundamental length measure for
        natural geometric interpretations of vector spaces. For a vector space
        of dimension *n*, the Euclidean norm is defined by: [#euclidnorm]_

        .. math::
            \|\vec{x}\|_{2}
                := \left(\sum_{i=1}^{n}|x_{i}|^{2}\right)^{1/2}

        The Euclidean norm equals the :term:`p-norm` for :math:`p=2` and induces
        a the :term:`Euclidean distance` to it's domain.

    Frobenius Distance
        The *Frobenius Distance* is a distance measure for matrices. For a
        vector space of dimension :math:`n \times m`, the Frobenius distance is
        defined by: [#frobenius]_

        .. math::
            d_{F}(A,\,B)
                := {\left(\sum_{i=1}^{m}\sum_{j=1}^{n}
                    |b_{ij} - a_{ij}|^{2}\right)}^{1/2}

        The Frobenius distance is induced by the :term:`Frobenius norm` and
        specifies the :term:`pq-mdistance` for the case :math:`p=q=1`.

    Frobenius Norm
        The *Frobenius norm* is a matrix norm, which is derived by the
        consecutive evaluation of the :term:`Euclidean norm` for the rows and
        columns of a matrix. For an underlying vector space of dimension
        :math:`n \times m`, the Frobenius norm is defined by: [#frobenius]_

        .. math::
            \|A\|_{F}
                := {\left(\sum_{i=1}^{m}\sum_{j=1}^{n}
                    |a_{ij}|^{2}\right)}^{1/2}

        The Frobenius norm specifies the :term:`pq-norm` for the case
        :math:`p=q=2`.

    Hölder Mean
        The *Hölder means* generalize the *Arithmetic mean* and the *Geometric
        mean*, in the same way as the :term:`p-norm` generalizes the
        :term:`Euclidean norm` and the :term:`1-norm`. For a positive
        real number *p* and a vector space of dimension *n*, the
        Hölder mean for absolute values is defined by: [#powermean]_

        .. math::
            M_{p}(\vec{x})
                := \left({\frac{1}{n}}\sum_{i=1}^{n}|x_{i}|^{p}\right)^{1/p}

        By it's definition it follows, that for :math:`p \geq 1` the Hölder
        means for absolute values are linear related to the p-norms:

        .. math::
            M_{p}(\vec{x})
                = \left(\frac{1}{n}\right)^{1/p}\|\vec{x}\|_{p}

        As a consequence for :math:`p \geq 1` the Hölder means of absolute
        values are norms and thus induce distances to their underlying domains.
        These are occasionally referred as :term:`Power-Mean difference`.

        The Hölder means and their respective distances, have important
        applications in regression analysis. When applied to the components of a
        random sample, the Hölder means of absolute values are known as the
        absolute sample moments and their induces metrices provide normalized
        measures of statistical dispersion.

    Manhattan Distance
        The *Manhattan Distance* corresponds to the interpretation of vector
        spaces as orthogonal lattices. For a vector space of dimension *n*, the
        Manhattan distance is defined by: [#taxicab]_

        .. math::
            d_{1}(\vec{x},\,\vec{y})
                := \sum_{i=1}^{n}|y_{i}-x_{i}|

        The Manhattan distance is induced by the :term:`1-norm` and specifies
        the :term:`Minkowski distance` for :math:`p=1`. When applied to a fixed
        set of outcomes of a random variable, the Minkowski distance is a
        measure of :term:`discrepancy` and referred as
        :term:`Sum of Absolute Differences`.

    Maximum Norm
        The *Maximum norm* provides a length measure for vector spaces. For a
        vector space of dimension *n*, the Maximum norm is defined by:
        [#maxnorm]_

        .. math::
            \|\vec{x}\|_{\infty}
                := \underset{i}{\max}\left(|x_{i}|\right)

        The Maximum norm specifies the :term:`p-norm` for the case
        :math:`p\rightarrow\infty` and induces the :term:`Chebyshev distance`
        to it's domain.

    Mean Absolute
        The *Mean Absolute* provides a normalized length measure for the
        interpretation of vector spaces as orthogonal lattices. For a
        vector space of dimension *n*, it is defined by:

        .. math::
            M_{1}(\vec{x})
                := \frac{1}{n} \sum_{i=1}^{n}|x_i|

        The Mean Absolute specifies the :term:`Hölder mean` of absolute values
        for the case :math:`p=1` and is linear dependent to the :term:`1-norm`:

        .. math::
            M_{1}(\vec{x})
                = \frac{\|\vec{x}\|_{1}}{n}

        Due to this linear relationship the Mean Absolute is a valid vector
        space norm and thus induces a distance to it's underlying domain,
        which is referred as :term:`mean absolute difference`.

    Mean Absolute Difference
        The *Mean Absolute Difference* (MD) is a normalized distance measure
        for the interpretation of vector spaces as orthogonal lattices. For a
        vector space of dimension *n*, this distance is defined by:

        .. math::
            \mathrm{MD}_{1}(\vec{x},\,\vec{y})
                := \frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|

        The mean absolute difference is induced by the :term:`mean absolute`
        and specifies the :term:`Power-Mean difference` for the case
        :math:`p=1`. Furthermore the mean absolute difference is linear
        dependent to the :term:`Manhattan distance`:

        .. math::
            \mathrm{MD}_{1}(\vec{x},\,\vec{y})
                = \frac{d_{1}(\vec{x},\,\vec{y})}{n}

        The term 'mean absolute difference' is frequently associated with it's
        application to sampled values [#mad]_. In regression analysis it
        provides a consistent and unbiased estimator for the
        :term:`mean absolute error` of a predictor.

    Minkowski Distance
        The class of *Minkowski Distances* provides different geometric
        interpretations of vector spaces. For a real number :math:`p \geq 1` and
        a vector space of dimension *n*, the Minkowski distance is defined by:
        [#minkowski]_

        .. math::
            d_{p}(\vec{x},\,\vec{y})
                := \left(\sum_{i=1}^{n}|y_{i}-x_{i}|^{p}\right)^{1/p}

        The class of Minkowski distances is induced by the :term:`p-norm` and
        comprises the :term:`Euclidean distance` the :term:`Manhattan distance`
        and the :term:`Chebyshev distance`

    p-Norm
        The *p-norms* provide length measures for different geometric
        interpretations of vector spaces. For a real number :math:`p \geq 1`
        and a vector space of dimension *n*, the p-norm is defined by: [#pnorm]_

        .. math::
            \|\vec{x}\|_{p}
                := \left(\sum_{i=1}^{n} |x_{i}|^{p}\right)^{1/p}

        For :math:`0 \leq p < 1` an evaluation according to the p-norm does not
        satisfy the triangle inequality and yields a quasi-norm.

        The p-norms generalize the :term:`1-Norm`, the :term:`Euclidean Norm`
        and the :term:`Maximum Norm`. The class of distances, induced by the
        p-norms are referred as :term:`Minkowski distance`.

    pq-Distance
        The *pq-Distances* are matrix distances, which are derived by an
        elementwise application of the :term:`p-norm` to the rows of two
        matrices, followed by an elementwise application of another
        p-norm to the columns. For real numbers :math:`p,\,q \geq 1` and
        an underlying vector space of dimension :math:`n \times m`, the
        pq-distance is defined by: [#pqdistance]_

        .. math::
            d_{p,q}(A,\,B)
                := \left(\sum_{j=1}^{m}
                    \left(\sum_{i=1}^{n}|a_{ij}-b_{ij}|^{p}\right)^{q/p}
                    \right)^{1/q}

        For the case :math:`p = q = 2`, the pq-distance is also referred
        as :term:`Frobenius distance`.

        .. [#pqdistance]
            https://en.wikipedia.org/wiki/Matrix_norm#L2,1_and_Lp,q_norms

    pq-Norm
        The *pq-Norms* are matrix norms, which are derived by an elementwise
        application of the :term:`p-norm` to the rows of a matrix, followed by
        an elementwise application of another p-norm to the columns.
        For real numbers :math:`p,\,q \geq 1` and an underlying vector space of
        dimension :math:`n \times m`, the pq-norm is defined by: [#pqnorm]_

        .. math::
            \|A\|_{p,q}
                := \left(\sum_{j=1}^{m}
                    \left(\sum_{i=1}^{n}|a_{ij}|^{p}\right)^{q/p}\right)^{1/q}

        For the case :math:`p = q = 2`, the pq-norm is also referred as
        :term:`Frobenius norm`.

    Power-Mean Difference
        The *Power-Mean Differences* are normalized distance measures for
        different geometric interpretations of vector spaces. For a real number
        :math:`p \geq 1` and a vector space of dimension *n*, the
        Power-Mean difference is defined by:

        .. math::
            \mathrm{MD}_p(\vec{x},\,\vec{y})
                := \left(\frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|^p\right)^{1/p}

        The Power-Mean differences are induced by the :term:`Hölder mean`
        for absolute values and linear related to the
        :term:`Minkowski distance`:

        .. math::
            \mathrm{MD}_p(\vec{x},\,\vec{y})
                = \left(\frac{1}{n}\right)^{1/p}d_p(\vec{x},\,\vec{y})

        When applied to the components of a random sample, the Power-Mean
        differences are normalized measures of statistical dispersion.

    Quadratic Mean
        The *Quadratic Mean* is a normalized length measure for the geometric
        interpretation of vector spaces. For a vector space of dimension *n*,
        it is defined by: [#qmean]_

        .. math::
            M_{2}(\vec{x})
                := \left({\frac{1}{n}}\sum_{i=1}^{n}|x_{i}|^{2}\right)^{1/2}

        The quadratic mean specifies the :term:`Hölder mean` for :math:`p=2` and
        is linear dependent to the :term:`Euclidean norm`:

        .. math::
            M_{2}(\vec{x})
                = \frac{\|\vec{x}\|_{2}}{\sqrt{n}}

        Due to this linear relationship the quadratic mean is a valid
        vector space norm and thus induces a distance to it's underlying domain,
        which occasionally is referred as the :term:`quadratic mean difference`.
        When applied to the components of a random sample, the quadratic mean
        norm is a sample statistic, which is referred as
        :term:`Root-Mean-Square`.

    Quadratic Mean Difference
        The *Quadratic Mean Difference* is a normalized distance measure
        for the natural geometric interpretation of vector spaces. For a
        vector space of dimension *n*, the distance is defined by:

        .. math::
            \mathrm{MD}_2(\vec{x},\,\vec{y})
                := {\left(\frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|\right)}^{1/2}

        The quadratic mean difference is induced by the :term:`quadratic mean`
        and specifies the :term:`Power-Mean difference` for the case
        :math:`p=2`. Furthermore the quadratic mean difference is linear
        dependent to the :term:`Euclidean distance`:

        .. math::
            \mathrm{MD}_{2}(\vec{x},\,\vec{y})
                = \frac{d_2(\vec{x},\,\vec{y})}{\sqrt{n}}

        When applied to individual components of a random sample, the
        quadratic mean difference is a measure of statistical dispersion and
        referred as :term:`Root-Mean-Square Error`.

.. rubric:: References
.. [#pnorm] https://en.wikipedia.org/wiki/P_norm
.. [#pqnorm] https://en.wikipedia.org/wiki/Matrix_norm#L2,1_and_Lp,q_norms
.. [#frobenius] https://en.wikipedia.org/wiki/Frobenius_norm
.. [#taxicab] https://en.wikipedia.org/wiki/Taxicab_geometry
.. [#euclidnorm] https://en.wikipedia.org/wiki/Euclidean_norm
.. [#maxnorm] https://en.wikipedia.org/wiki/Maximum_norm
.. [#powermean] https://en.wikipedia.org/wiki/Power_mean
.. [#qmean] https://en.wikipedia.org/wiki/Quadratic_mean
.. [#minkowski] https://en.wikipedia.org/wiki/Minkowski_distance
.. [#euclid] https://en.wikipedia.org/wiki/Euclidean_distance
.. [#chebyshev] https://en.wikipedia.org/wiki/Chebyshev_distance
.. [#mad] https://en.wikipedia.org/wiki/Mean_absolute_difference
.. [#leastsquares] https://en.wikipedia.org/wiki/Least_squares

Regression
----------

.. glossary::

    Discrepancy
        A *discrepancy* is a binary function in a space of random variables,
        that induces a semi-metric to the underlying space. [#discrepancy]_ In
        regression analysis discrepancies are used to assess the accuracy of a
        predictor, by quantifying the expected deviation between observed and
        predicted realizations. By minimizing a discrepancy with respect to
        parameters, it serves as an objective function for parameter and model
        selection.

    Sum of Absolute Differences
        The *Sum of Absolute Differences* (SAD) is a measure of
        :term:`discrepancy`, that assesses the accuracy of a predictor with
        respect to a fixed (finite) set of observations. For an
        observable random variable :math:`Y` with *n* fixed observations
        :math:`\mathbf{y}` and a predictor :math:`\hat{Y}` with corresponding
        predictions :math:`\hat{\mathbf{y}}` the RSS is given by:

        .. math::
            \mathrm{SAD}(\mathbf{y},\,\hat{\mathbf{y}})
                := \sum_{i=1}^{n}|y_{i}-\hat{y}_{i}|

        The SAD equals the :term:`Manhattan distance` and therefore is also a
        valid distance measure within the underlying space of random variables.
        The SAD is effectively the simplest possible distance, that takes into
        account every observation of a fixed finite set. This makes SAD an
        extremely fast distance measure.

    Residual Sum of Squares
        The *Residual Sum of Squares* (RSS) is a measure of
        :term:`discrepancy`, that assesses the accuracy of a predictor with
        respect to a fixed (finite) set of observations. For an
        observable random variable :math:`Y` with *n* fixed observations
        :math:`\mathbf{y}` and a predictor :math:`\hat{Y}` with corresponding
        predictions :math:`\hat{\mathbf{y}}` the RSS is given by:

        .. math::
            \mathrm{RSS}(\mathbf{y},\,\hat{\mathbf{y}})
                := \sum_{i=1}^{n}(y_{i}-\hat{y}_{i})^2

        The RSS equals the squared :term:`Euclidean distance`, which does not
        satisfy the triangle inequality and therefore does not define a valid
        distance measure. Since the RSS, however, is positive definite and
        subhomogeneous, it induces a semi-metric to the underlying space of
        random variables.

    Mean Squared Error
        The *Mean Squared Error* (MSE) is a measure of :term:`discrepancy`,
        that assesses the accuracy of a predictor. For an observable random
        variable :math:`Y` and a corresponding predictor :math:`\hat{Y}` the MSE
        is defined by:

        .. math::
            \mathrm{MSE}
                := \mathrm{E}\left[(Y-\hat{Y})^2\right]

        The MSE has a consistent and unbiased estimator, given by the
        squared :term:`quadratic mean difference` of observations and
        predictions. For *n* observations :math:`\mathbf{y}` with corresponding
        predictions :math:`\hat{\mathbf{y}}` the MSE is estimated by:

        .. math::
            \mathrm{MD}_2(\mathbf{y},\,\hat{\mathbf{y}})^2
                \xrightarrow{\, n \to \infty \, } \mathrm{MSE}

        In difference to the :term:`Root-Mean-Square Error`, the MSE does not
        satisfy the triangle inequality and therefore does not define a valid
        distance measure. Since the MSE, however, is positive definite and
        subhomogeneous, it induces a semi-metric to the underlying space of
        random variables.

    Mean Absolute Error
        The *Mean Absolute Error* (MAE) is a measure of :term:`discrepancy`,
        that assesses the accuracy of a predictor. For an observable random
        variable :math:`Y` and a corresponding predictor :math:`\hat{Y}` the MAE
        is defined by:

        .. math::
            \mathrm{MAE}
                := \mathrm{E}\left[|Y-\hat{Y}|\right]

        The MAE has a consistent and unbiased estimator, given by the
        :term:`mean absolute difference` of observations and predictions. For
        *n* observations :math:`\mathbf{y}` with corresponding predictions
        :math:`\hat{\mathbf{y}}` the MAE is estimated by:

        .. math::
            \mathrm{MD}_1(\mathbf{y},\,\hat{\mathbf{y}})
                \xrightarrow{\, n \to \infty \, } \mathrm{MAE}

        Due to this transition, the MAE adopts all required properties from the
        mean absolute difference, to induce a valid metric to the space of
        random variables.

    Root-Mean-Square Error
        The *Root-Mean-Square Error* (RMSE) is a measure of :term:`discrepancy`,
        that assesses the accuracy of a predictor. For an observable random
        variable :math:`Y` and a corresponding predictor :math:`\hat{Y}` the
        RMSE is defined by:

        .. math::
            \mathrm{RMSE}
                := \mathrm{E}\left[(Y-\hat{Y})^2\right]^{1/2}

        The RMSE has a consistent and unbiased estimator, given by the
        :term:`quadratic mean difference` of observations and predictions. For
        *n* observations :math:`\mathbf{y}` with corresponding predictions
        :math:`\hat{\mathbf{y}}` the RMSE is estimated by:

        .. math::
            \mathrm{MD}_2(\mathbf{y},\,\hat{\mathbf{y}})
                \xrightarrow{\, n \to \infty \, } \mathrm{RMSE}

        Due to this transition, the RMSE adopts all required properties from the
        quadratic mean difference, to induce a valid metric to the space of
        random variables.

.. rubric:: References
.. [#discrepancy] https://en.wikipedia.org/wiki/discrepancy_function
