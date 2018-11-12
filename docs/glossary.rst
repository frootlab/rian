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
        induces a metric to it's underlying domain, which commonly is referred
        as the :term:`Manhattan metric`. When applied to the components of a
        random sample, the Manhattan metric is also known as the :term:`Sum of
        Absolute Differences`.

    Chebyshev Metric
        The *Chebyshev metric* provides a distance measure for vector spaces.
        For an underlying vector space of dimension *n*, the Chebyshev distance
        is defined by: [#chebyshev]_

        .. math::
            d_{\infty}(\vec{x},\,\vec{y})
                := \underset{i}{\max}\left(|y_{i}-x_{i}|\right)

        The Chebyshev metric is induced by the :term:`Maximum norm` and
        specifies the :term:`Minkowski metric` for the case
        :math:`p\rightarrow\infty`.

    Euclidean Metric
        The *Euclidean metric* provides a distance measure for the natural
        geometric interpretation of vector spaces. For a vector space of
        dimension *n*, the Euclidean distance is defined by: [#euclid]_

        .. math::
            d_{2}(\vec{x},\,\vec{y})
                := \left(\sum_{i=1}^{n}|y_{i}-x_{i}|^{2}\right)^{1/2}

        The Euclidean metric is induced by the :term:`Euclidean norm` and
        specifies the :term:`Minkowski metric` for the case :math:`p=2`. With
        respect to regression analysis the Euclidean metric endows the
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
        a metric to it's domain which is known as the :term:`Euclidean metric`.
        When applied to the components of a random sample, the Euclidean metric
        is usually referred as the :term:`Root-Sum-Square Difference` (RSSD),
        which i.e. is used in the method of least squares.

    Frobenius Metric
        The *Frobenius metric* provides a distance measure for matrices. For a
        vector space of dimension :math:`n \times m`, the Frobenius distance is
        defined by: [#frobenius]_

        .. math::
            d_{F}(A,\,B)
                := {\left(\sum_{i=1}^{m}\sum_{j=1}^{n}
                    |b_{ij} - a_{ij}|^{2}\right)}^{1/2}

        The Frobenius metric is induced by the :term:`Frobenius norm` and
        specifies the :term:`pq-metric` for the case :math:`p=q=1`.

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

        It can be concluded, that for :math:`p \geq 1` the Hölder means of
        absolute values are norms and thus induce metrices to their underlying
        domains. These are occasionally referred as
        :term:`Power-Mean difference`.

        The Hölder means and their respective metrices, have important
        applications in regression analysis. When applied to the components of a
        random sample, the Hölder means of absolute values are known as the
        absolute sample moments and their induces metrices provide normalized
        measures of statistical dispersion.

    Manhattan Metric
        The *Manhattan metric* provides a distance measure for the
        interpretation of vector spaces as orthogonal lattices. For a vector
        space of dimension *n*, the Manhattan distance is defined by:
        [#taxicab]_

        .. math::
            d_{1}(\vec{x},\,\vec{y})
                := \sum_{i=1}^{n}|y_{i}-x_{i}|

        The Manhattan metric is induced by the :term:`1-norm` and a special
        case of the :term:`Minkowski metric` for :math:`p=1`. When applied to
        the components of a random sample, the Manhattan metric is commonly
        referred as :term:`Sum of Absolute Differences`.

    Maximum Norm
        The *Maximum norm* provides a length measure for vector spaces. For a
        vector space of dimension *n*, the Maximum norm is defined by:
        [#maxnorm]_

        .. math::
            \|\vec{x}\|_{\infty}
                := \underset{i}{\max}\left(|x_{i}|\right)

        The Maximum norm specifies the :term:`p-norm` for the case
        :math:`p\rightarrow\infty` and induces a metric to it's domain,
        which generally is referred as :term:`Chebyshev metric`

    Mean-Absolute
        The *Mean-Absolute* provides a normalized length measure for the
        interpretation of vector spaces as orthogonal lattices. For a
        vector space of dimension *n*, it is defined by:

        .. math::
            M_{1}(\vec{x})
                := \frac{1}{n} \sum_{i=1}^{n}|x_i|

        The Mean-Absolute specifies the :term:`Hölder mean` of absolute values
        for the case :math:`p=1` and is linear dependent to the :term:`1-norm`:

        .. math::
            M_{1}(\vec{x})
                = \frac{\|\vec{x}\|_{1}}{n}

        Due to this linear relationship the Mean-Absolute is a valid vector
        space norm and thus induces a metric to it's underlying domain,
        which occasionally is referred as the :term:`Mean-Absolute difference`.

    Mean-Absolute Difference
        The *Mean-Absolute difference* provides a normalized distance
        measure for the interpretation of vector spaces as orthogonal lattices.
        For a vector space of dimension *n*, this distance is defined by:

        .. math::
            \mathrm{MD}_{1}(\vec{x},\,\vec{y})
                := \frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|

        The Mean-Absolute difference is induced by the :term:`Mean-Absolute`
        and specifies the :term:`Power-Mean difference` for the case
        :math:`p=1`. Furthermore the Mean-Absolute difference is linear
        dependent to the :term:`Manhattan metric`:

        .. math::
            \mathrm{MD}_{1}(\vec{x},\,\vec{y})
                = \frac{d_{1}(\vec{x},\,\vec{y})}{n}

        The term 'Mean-Absolute difference' is usually associated with it's
        application to the components of a random sample [#mad]_. With respect
        to regression analysis it provides a discrepancy measure, between
        observed and estimated realizations and is commonly referred as the
        :term:`Mean-Absolute Error`.

    Minkowski Metric
        The class of *Minkowski metrices* provides distance measures for
        different geometric interpretations of vector spaces. For a real
        number :math:`p \geq 1` and a vector space of dimension *n*, the
        respective Minkowski distance is defined by: [#minkowski]_

        .. math::
            d_{p}(\vec{x},\,\vec{y})
                := \left(\sum_{i=1}^{n}|y_{i}-x_{i}|^{p}\right)^{1/p}

        The Minkowski metrices are induced by the :term:`p-norm` and comprise
        the :term:`Euclidean metric` the :term:`Manhattan metric` and the
        :term:`Chebyshev metric`

    p-Norm
        The *p-norms* provide length measures for different geometric
        interpretations of vector spaces. For a real number :math:`p \geq 1`
        and a vector space of dimension *n*, the p-norm is defined by: [#pnorm]_

        .. math::
            \|\vec{x}\|_{p}
                := \left(\sum_{i=1}^{n} |x_{i}|^{p}\right)^{1/p}

        The p_norms generalize the :term:`1-Norm`, the :term:`Euclidean Norm`
        and the :term:`Maximum Norm`. The metrices, induced by the p-norms
        are referred as :term:`Minkowski metric`.

    pq-Norm
        The *pq-norms* are matrix norms, which are derived by consecutively
        applying a respective :term:`p-norm` to the rows and the columns of a
        matrix. For real numbers :math:`p,\,q \geq 1` and a vector space of
        dimension :math:`n \times m`, the pq-norms are defined by: [#pqnorm]_

        .. math::
            \|A\|_{p,q}
                := \left(\sum_{j=1}^{m}
                    \left(\sum_{i=1}^{n}|a_{ij}|^{p}\right)^{q/p}\right)^{1/q}

        For the case that :math:`p = q = 2`, the respective pq-norm is referred
        as the :term:`Frobenius norm`.

    Power-Mean Difference
        The *Power-Mean Differences* provide normalized distance measures for
        different geometric interpretations of vector spaces. For a real number
        :math:`p \geq 1` and a vector space of dimension *n*, the
        Power-Mean difference is defined by:

        .. math::
            \mathrm{MD}_p(\vec{x},\,\vec{y})
                := \left(\frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|^p\right)^{1/p}

        The Power-Mean differences are induced by the :term:`Hölder mean`
        for absolute values and linear related to the :term:`Minkowski Metric`:

        .. math::
            \mathrm{MD}_p(\vec{x},\,\vec{y})
                = \left(\frac{1}{n}\right)^{1/p}d_p(\vec{x},\,\vec{y})

        When applied to the components of a random sample, the Power-Mean
        differences are normalized measures of statistical dispersion.

    Quadratic-Mean
        The *Quadratic-Mean* is a normalized length measure for the geometric
        interpretation of vector spaces. For a vector space of dimension *n*,
        it is defined by: [#qmean]_

        .. math::
            M_{2}(\vec{x})
                := \left({\frac{1}{n}}\sum_{i=1}^{n}|x_{i}|^{2}\right)^{1/2}

        The Mean-Absolute specifies the :term:`Hölder mean` of absolute values
        for the case :math:`p=2` and is linear dependent to the
        :term:`Euclidean norm`:

        .. math::
            M_{2}(\vec{x})
                = \frac{\|\vec{x}\|_{2}}{\sqrt{n}}

        Due to this linear relationship the Quadratic-Mean is a valid
        vector space norm and thus induces a metric to it's underlying domain,
        which occasionally is referred as the :term:`Quadratic-Mean difference`.
        When applied to the components of a random sample, the Quadratic-Mean
        norm is a sample statistic, which is referred as
        :term:`Root-Mean-Square`.

    Quadratic-Mean Difference
        The *Quadratic-Mean difference* provides a normalized distance measure
        for the natural geometric interpretation of vector spaces. For a
        vector space of dimension *n*, the distance is defined by:

        .. math::
            \mathrm{MD}_2(\vec{x},\,\vec{y})
                := {\left(\frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|\right)}^{1/2}

        The Quadratic-Mean difference is induced by the :term:`Quadratic-Mean`
        and specifies the :term:`Power-Mean difference` for the case
        :math:`p=2`. Furthermore the Quadratic-Mean difference is linear
        dependent to the :term:`Euclidean metric`:

        .. math::
            \mathrm{MD}_{2}(\vec{x},\,\vec{y})
                = \frac{d_2(\vec{x},\,\vec{y})}{\sqrt{n}}

        When applied to individual components of a random sample, the
        Quadratic-Mean difference is a measure of statistical dispersion and
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
