Glossary
========

Math Glossary
-------------

Norms and Metrices
~~~~~~~~~~~~~~~~~~

.. glossary::

    1-Norm
        The *1-norm* provides a length measure for the interpretation of
        vector spaces as orthogonal lattices. For a vector space of dimension
        *n*, the norm is given by: [#]_

        .. math::
            \|\vec{x}\|_{1}
                := \sum_{i=1}^{n} |x_{i}|

        The 1-norm specifies the :term:`p-norm` for the case :math:`p=1` and
        induces the :term:`Manhattan distance` to the underlying vector space.
        When applied to a random sample, the Manhattan distance is also known as
        the :term:`sum of absolute differences`.

        .. rubric:: References
        .. [#] https://en.wikipedia.org/wiki/Taxicab_geometry

    Chebyshev Distance
        The *Chebyshev Distance* generates the *Chebyshev Metric*. For a
        vector space of dimension *n*, the Chebyshev distance is given by:
        [#]_

        .. math::
            d_{\infty}(\vec{x},\,\vec{y})
                := \underset{i}{\max}\left(|y_{i}-x_{i}|\right)

        The Chebyshev distance is induced by the :term:`Maximum norm` and
        specifies the :term:`Minkowski distance` for the transition
        :math:`p\rightarrow\infty`.

        .. [#] https://en.wikipedia.org/wiki/Chebyshev_distance

    Euclidean Distance
        The *Euclidean Distance* corresponds to the natural geometric
        interpretation of a vector space. For an underlying vector space of
        dimension *n*, the Euclidean distance is given by: [#]_

        .. math::
            d_{2}(\vec{x},\,\vec{y})
                := \left(\sum_{i=1}^{n}|y_{i}-x_{i}|^{2}\right)^{1/2}

        The Euclidean distance is induced by the :term:`Euclidean norm` and
        specifies the :term:`Minkowski distance` for the case :math:`p=2`. With
        respect to regression analysis the Euclidean distance endows the
        components of a random sample with a discrepancy measure,
        between observed an estimated realizations. This discrepancy measure is
        commonly referred as :term:`Residual sum of squares` (RSS) and provides
        the foundation for the method of least squares. [#]_

        .. [#] https://en.wikipedia.org/wiki/Euclidean_distance
        .. [#] https://en.wikipedia.org/wiki/Least_squares

    Euclidean Norm
        The *Euclidean norm* provides the fundamental length measure for
        natural geometric interpretations of vector spaces. For a vector space
        of dimension *n*, the Euclidean norm is given by: [#]_

        .. math::
            \|\vec{x}\|_{2}
                := \left(\sum_{i=1}^{n}|x_{i}|^{2}\right)^{1/2}

        The Euclidean norm equals the :term:`p-norm` for :math:`p=2` and induces
        a the :term:`Euclidean distance` to it's domain.

        .. [#] https://en.wikipedia.org/wiki/Euclidean_norm

    Frobenius Distance
        The *Frobenius Distance* is a distance measure for matrices. For a
        vector space of dimension :math:`n \times m`, the Frobenius distance is
        defined by: [#]_

        .. math::
            d_{F}(A,\,B)
                := {\left(\sum_{i=1}^{m}\sum_{j=1}^{n}
                    |b_{ij} - a_{ij}|^{2}\right)}^{1/2}

        The Frobenius distance is induced by the :term:`Frobenius norm` and
        specifies the :term:`pq-distance` for the case :math:`p=q=1`.

        .. [#] https://en.wikipedia.org/wiki/Frobenius_norm

    Frobenius Norm
        The *Frobenius norm* is a matrix norm, which is derived by the
        consecutive evaluation of the :term:`Euclidean norm` for the rows and
        columns of a matrix. For an underlying vector space of dimension
        :math:`n \times m`, the Frobenius norm is given by: [#]_

        .. math::
            \|A\|_{F}
                := {\left(\sum_{i=1}^{m}\sum_{j=1}^{n}
                    |a_{ij}|^{2}\right)}^{1/2}

        The Frobenius norm specifies the :term:`pq-norm` for the case
        :math:`p=q=2`.

        .. [#] https://en.wikipedia.org/wiki/Frobenius_norm

    Hölder Mean
        The *Hölder means* generalize the *Arithmetic mean* and the *Geometric
        mean*, in the same way as the :term:`p-norm` generalizes the
        :term:`Euclidean norm` and the :term:`1-norm`. For a positive real
        number *p* and a vector space of dimension *n*, the Hölder mean for
        absolute values is given by: [#]_

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
        These are occasionally referred as :term:`power mean difference`.

        The Hölder means and their respective distances, have important
        applications in regression analysis. When applied to the components of a
        random sample, the Hölder means of absolute values are known as the
        absolute sample moments and their induces metrices provide normalized
        measures of statistical dispersion.

        .. [#] https://en.wikipedia.org/wiki/Power_mean

    Manhattan Distance
        The *Manhattan Distance* corresponds to the interpretation of vector
        spaces as orthogonal lattices. For a vector space of dimension *n*, the
        Manhattan distance is given by: [#]_

        .. math::
            d_{1}(\vec{x},\,\vec{y})
                := \sum_{i=1}^{n}|y_{i}-x_{i}|

        The Manhattan distance is induced by the :term:`1-norm` and specifies
        the :term:`Minkowski distance` for :math:`p=1`. When applied to a fixed
        set of outcomes of a random variable, the Minkowski distance is a
        measure of :term:`discrepancy measure` and referred as :term:`Sum of
        Absolute Differences`.

        .. [#] https://en.wikipedia.org/wiki/Taxicab_geometry

    Maximum Norm
        The *Maximum norm* provides a length measure for vector spaces. For a
        vector space of dimension *n*, the Maximum norm is given by: [#]_

        .. math::
            \|\vec{x}\|_{\infty}
                := \underset{i}{\max}\left(|x_{i}|\right)

        The Maximum norm specifies the :term:`p-norm` for the case
        :math:`p\rightarrow\infty` and induces the :term:`Chebyshev distance`
        to it's domain.

        .. [#] https://en.wikipedia.org/wiki/Maximum_norm

    Mean Absolute
        The *Mean Absolute* provides a normalized length measure for the
        interpretation of vector spaces as orthogonal lattices. For a
        vector space of dimension *n*, it is given by:

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
        vector space of dimension *n*, this distance is given by:

        .. math::
            \mathrm{MD}_{1}(\vec{x},\,\vec{y})
                := \frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|

        The mean absolute difference is induced by the :term:`mean absolute`
        and specifies the :term:`power mean difference` for the case
        :math:`p=1`. Furthermore the mean absolute difference is linear
        dependent to the :term:`Manhattan distance`:

        .. math::
            \mathrm{MD}_{1}(\vec{x},\,\vec{y})
                = \frac{d_{1}(\vec{x},\,\vec{y})}{n}

        The term 'mean absolute difference' is frequently associated with it's
        application to sampled values [#]_. In regression analysis it
        provides a consistent and unbiased estimator for the
        :term:`mean absolute error` of a predictor.

        .. [#] https://en.wikipedia.org/wiki/Mean_absolute_difference

    Minkowski Distance
        The class of *Minkowski Distances* provides different geometric
        interpretations of vector spaces. For a real number :math:`p \geq 1` and
        a vector space of dimension *n*, the Minkowski distance is given by:
        [#]_

        .. math::
            d_{p}(\vec{x},\,\vec{y})
                := \left(\sum_{i=1}^{n}|y_{i}-x_{i}|^{p}\right)^{1/p}

        The class of Minkowski distances is induced by the :term:`p-norm` and
        comprises the :term:`Euclidean distance` the :term:`Manhattan distance`
        and the :term:`Chebyshev distance`

        .. [#] https://en.wikipedia.org/wiki/Minkowski_distance

    p-Norm
        The *p-norms* provide length measures for different geometric
        interpretations of vector spaces. For a real number :math:`p \geq 1`
        and a vector space of dimension *n*, the p-norm is given by: [#]_

        .. math::
            \|\vec{x}\|_{p}
                := \left(\sum_{i=1}^{n} |x_{i}|^{p}\right)^{1/p}

        For :math:`0 \leq p < 1` an evaluation according to the p-norm does not
        satisfy the triangle inequality and yields a quasi-norm.

        The p-norms generalize the :term:`1-Norm`, the :term:`Euclidean Norm`
        and the :term:`Maximum Norm`. The class of distances, induced by the
        p-norms are referred as :term:`Minkowski distance`.

        .. [#] https://en.wikipedia.org/wiki/P_norm

    pq-Distance
        The *pq-Distances* are matrix distances, which are derived by an
        elementwise application of the :term:`p-norm` to the rows of two
        matrices, followed by an elementwise application of another
        p-norm to the columns. For real numbers :math:`p,\,q \geq 1` and
        an underlying vector space of dimension :math:`n \times m`, the
        pq-distance is given by: [#]_

        .. math::
            d_{p,q}(A,\,B)
                := \left(\sum_{j=1}^{m}
                    \left(\sum_{i=1}^{n}|a_{ij}-b_{ij}|^{p}\right)^{q/p}
                    \right)^{1/q}

        For the case :math:`p = q = 2`, the pq-distance is also referred
        as :term:`Frobenius distance`.

        .. [#] https://en.wikipedia.org/wiki/Matrix_norm#L2,1_and_Lp,q_norms

    pq-Norm
        The *pq-Norms* are matrix norms, which are derived by an elementwise
        application of the :term:`p-norm` to the rows of a matrix, followed by
        an elementwise application of another p-norm to the columns.
        For real numbers :math:`p,\,q \geq 1` and an underlying vector space of
        dimension :math:`n \times m`, the pq-norm is given by: [#]_

        .. math::
            \|A\|_{p,q}
                := \left(\sum_{j=1}^{m}
                    \left(\sum_{i=1}^{n}|a_{ij}|^{p}\right)^{q/p}\right)^{1/q}

        For the case :math:`p = q = 2`, the pq-norm is also referred as
        :term:`Frobenius norm`.

        .. [#] https://en.wikipedia.org/wiki/Matrix_norm#L2,1_and_Lp,q_norms

    Power Mean Difference
        The *Power Mean Differences* are normalized distance measures for
        different geometric interpretations of vector spaces. For a real number
        :math:`p \geq 1` and a vector space of dimension *n*, the
        power mean difference is given by:

        .. math::
            \mathrm{MD}_p(\vec{x},\,\vec{y})
                := \left(\frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|^p\right)^{1/p}

        The power mean differences are induced by the :term:`Hölder mean`
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
        it is given by: [#]_

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
        :term:`Root-Mean-Square error`.

        .. [#] https://en.wikipedia.org/wiki/Quadratic_mean

    Quadratic Mean Difference
        The *Quadratic Mean Difference* is a normalized distance measure
        for the natural geometric interpretation of vector spaces. For a
        vector space of dimension *n*, the distance is given by:

        .. math::
            \mathrm{MD}_2(\vec{x},\,\vec{y})
                := {\left(\frac{1}{n}\sum_{i=1}^n|y_{i}-x_{i}|\right)}^{1/2}

        The quadratic mean difference is induced by the :term:`quadratic mean`
        and specifies the :term:`power mean difference` for :math:`p=2`.
        Furthermore the quadratic mean difference is linear dependent to the
        :term:`Euclidean distance`:

        .. math::
            \mathrm{MD}_{2}(\vec{x},\,\vec{y})
                = \frac{d_2(\vec{x},\,\vec{y})}{\sqrt{n}}

        When applied to individual components of a random sample, the
        quadratic mean difference is a measure of statistical dispersion and
        referred as :term:`Root-Mean-Square Error`.

Statistics
~~~~~~~~~~

.. glossary::

    Association Measure
        *Association measures* refer to a wide variety of coefficients,
        that measure the statistical strength of relationships between the
        variables of interest. These measures can be directed / undirected,
        signed / unsigned and normalized or unnormalized. Examples for
        association measures are the Pearson correlation coefficient, Mutual
        information or Statistical Interactions.

    Discrepancy Measure
        *Discrepancy measures* are binary functions in spaces of random
        variables, that induce a semi-metric to the underlying space.
        [#]_ In regression analysis discrepancies are used to assess
        the accuracy of a predictor, by quantifying the expected deviation
        between observed and predicted realizations. By minimizing a discrepancy
        with respect to parameters, it serves as an objective function for
        parameter and model selection.

        .. [#] https://en.wikipedia.org/wiki/discrepancy_function

    Mean Absolute Error
        The *Mean Absolute Error* (MAE) is a :term:`discrepancy measure`,
        that assesses the accuracy of a predictor. For an observable random
        variable :math:`Y` and a corresponding predictor :math:`\hat{Y}` the MAE
        is given by:

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

    Mean Squared Error
        The *Mean Squared Error* (MSE) is a :term:`discrepancy measure`,
        that assesses the accuracy of a predictor. For an observable random
        variable :math:`Y` and a corresponding predictor :math:`\hat{Y}` the MSE
        is given by:

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

    Residual Sum of Squares
        The *Residual Sum of Squares* (RSS) is a :term:`discrepancy measure`,
        that assesses the accuracy of a predictor with respect to a fixed
        (finite) set of observations. For an observable random variable
        :math:`Y` with *n* fixed observations :math:`\mathbf{y}` and a predictor
        :math:`\hat{Y}` with corresponding predictions :math:`\hat{\mathbf{y}}`
        the RSS is given by:

        .. math::
            \mathrm{RSS}(\mathbf{y},\,\hat{\mathbf{y}})
                := \sum_{i=1}^{n}(y_{i}-\hat{y}_{i})^2

        The RSS equals the squared :term:`Euclidean distance`, which does not
        satisfy the triangle inequality and therefore does not define a valid
        distance measure. Since the RSS, however, is positive definite and
        subhomogeneous, it induces a semi-metric to the underlying space of
        random variables.

    Root-Mean-Square Error
        The *Root-Mean-Square Error* (RMSE) is a :term:`discrepancy measure`,
        that assesses the accuracy of a predictor. For an observable random
        variable :math:`Y` and a corresponding predictor :math:`\hat{Y}` the
        RMSE is given by:

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

    Sum of Absolute Differences
        The *Sum of Absolute Differences* (SAD) is a :term:`discrepancy
        measure`, that assesses the accuracy of a predictor with respect to a
        fixed (finite) set of observations. For an observable random variable
        :math:`Y` with *n* fixed observations :math:`\mathbf{y}` and a predictor
        :math:`\hat{Y}` with corresponding predictions :math:`\hat{\mathbf{y}}`
        the RSS is given by:

        .. math::
            \mathrm{SAD}(\mathbf{y},\,\hat{\mathbf{y}})
                := \sum_{i=1}^{n}|y_{i}-\hat{y}_{i}|

        The SAD equals the :term:`Manhattan distance` and therefore is also a
        valid distance measure within the underlying space of random variables.
        The SAD is effectively the simplest possible distance, that takes into
        account every observation of a fixed finite set. This makes SAD an
        extremely fast distance measure.

API Glossary
------------

Types
~~~~~

.. glossary::

    File Reference

        *File references* aggregate different types, that identify files,
        including: :term:`File objects <file object>`, Strings and
        :term:`path-like objects <path-like object>`, that point to filenames in
        the directory structure of the system and instances of the class
        :class:`~nemoa.types.FileAccessorBase`.

    Row Like

        *Row like* data comprises different data formats, which are used to
        represent table records. This includes tuples, mappings and instances of
        the :class:`Record class <nemoa.db.table.Record>`. The :class:`Table
        class <nemoa.db.table.Table>` accepts these data types for appending
        rows by :meth:`~nemoa.db.table.Table.insert` and for retrieving rows by
        :meth:`~nemoa.db.table.Table.select`.

    Cursor Mode

        The *cursor mode* defines the *scrolling type* and the *operation mode*
        of a cursor. Internally the respective parameters of the
        :class:`Cursor class <nemoa.db.table.Cursor>` are identified by binary
        flags. The public interface uses a string representation, given by
        the space separated names of the scrolling type and the the operation
        mode. Supported scrolling types are:

        :forward-only: The default scrolling type of cursors is called a
            forward-only cursor and can move only forward through the result
            set. A forward-only cursor does not support scrolling but only
            fetching rows from the start to the end of the result set.
        :scrollable: A scrollable cursor is commonly used in screen-based
            interactive applications, like spreadsheets, in which users are
            allowed to scroll back and forth through the result set. However,
            applications should use scrollable cursors only when forward-only
            cursors will not do the job, as scrollable cursors are generally
            more expensive, than forward-only cursors.
        :random: Random cursors move randomly through the result set. In
            difference to a randomly sorted cursor, the rows are not unique and
            the number of fetched rows is not limited to the size of the result
            set. If the method :meth:`.fetch` is called with a zero value for
            size, a CursorModeError is raised.

        Supported operation modes are:

        :dynamic: A **dynamic cursor** is built on-the-fly and therefore
            comprises any changes made to the rows in the result set during it's
            traversal, including new appended rows and the order of it's
            traversal. This behavior is regardless of whether the changes occur
            from inside the cursor or by other users from outside the cursor.
            Dynamic cursors are thread-safe but do not support counting filtered
            rows or sorting rows.
        :indexed: Indexed cursors (aka Keyset-driven cursors) are built
            on-the-fly with respect to an initial copy of the table index and
            therefore comprise changes made to the rows in the result set during
            it's traversal, but not new appended rows nor changes within their
            order. Keyset driven cursors are thread-safe but do not support
            sorting rows or counting filtered rows.
        :static: Static cursors are buffered and built during it's creation time
            and therefore always display the result set as it was when the cursor
            was first opened. Static cursors are not thread-safe but support
            counting the rows with respect to a given filter and sorting the
            rows.
