r"""
This module implements lattices of torsion classes of an abelian length category
in case they are finite.

This module defines :class: `FiniteTorsLattice`, which is a subclass of
:class:`sage.combinat.posets.lattices.FiniteLatticePoset`,
together with various methods which are useful in the study of
the representation theory of algebras.

Requirement: SageMath ver 9.x or later
"""
# *****************************************************************************
#       Copyright (C) 2021 Haruhisa Enomoto <the35883@osakafu-u.ac.jp>
#
# GitHub Repository:
# https://github.com/haruhisa-enomoto/tors-lattice
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.0
#                  https://www.gnu.org/licenses/
#
# Any feedback is welcome!
# *****************************************************************************
import sage.all
from sage.misc.cachefunc import cached_method
from sage.combinat.posets.lattices import FiniteLatticePoset, LatticePoset
from sage.combinat.posets.posets import Poset
from sage.homology.simplicial_complex import SimplicialComplex

def _kappa(lattice, j):
    r"""
    Return `\kappa(j)` for a join-irreducible element `j`
    in a finite lattice ``lattice`` if it exists.

    INPUT:

    - ``lattice`` -- a finite lattice,
      which should be an instance of
      :class:`sage.combinat.posets.lattices.FiniteLatticePoset`

    - ``j`` -- an element of ``lattice``,
      which is expected to be join-irreducible

    OUTPUT:

    an element of ``lattice``, or ``None`` if it does not exist.

    .. SEEALSO::
      :meth:`sage.combinat.posets.hasse_diagram.HasseDiagram.kappa`
    """
    hasse = lattice._hasse_diagram
    j_vtx = lattice._element_to_vertex(j)
    m_vtx = hasse.kappa(j_vtx)
    if m_vtx is None:
        return None
    m = lattice._vertex_to_element(m_vtx)
    return m

def _extended_kappa(lattice, x):
    r"""
    Return `\overline{\kappa(x)}` for an element `x`
    in a finite lattice ``lattice`` if it exists.

    This first computes the canonical joinands of `x`,
    and then computes the meet of kappa of them.
    This returns ``None`` if ``x`` admits no canonical join reprensetation
    or kappa of some canonical joinand does not exist.

    INPUT:

    - ``lattice`` -- a finite lattice,
      which should be an instance of
      :class:`sage.combinat.posets.lattices.FiniteLatticePoset`

    - ``x`` -- an element of ``lattice``

    OUTPUT:

    an element of ``lattice``, or ``None`` if it does not exist.

    REFERENCES:

    .. [BTZ] E. Barnard, G. Todorov, S. Zhu,
       Dynamical combinatorics and torsion classes,
       J. Pure Appl. Algebra 225 (2021), no. 9, 106642.

    """
    CJR = lattice.canonical_joinands(x)
    if CJR is None:
        return None
    kappa_CJR = [_kappa(lattice, j) for j in CJR]
    try:
        return lattice.meet(kappa_CJR)
    except:
        return None

def myshow(poset, label = True, vertex_size = 100, **kwargs):
    r"""
    A variant of ``show`` method, which looks nicer for the Hasse diagram of a poset.

    NOTE that the direction of Hasse arrows in SageMath is opposite to
    the representation-threorist's convention, that is,
    there is an arrow $p \to q$ if $p$ is covered by $q$.

    INPUT:

    - ``poset`` -- an object which has ``show`` method,
      which we expect to be an instance of
      :class:`sage.combinat.posets.posets.FinitePosets`

    - ``label`` -- a Boolean (default: ``True``), whether to label vertices

    - ``vertex_size`` -- the size of vertices (default: 100)

    - ``**kwargs`` -- keyword arguments that will passed down to `poset.show()`,
      see :meth:`sage.combinat.posets.posets.FinitePoset.show`
    """
    if label:
        poset.show(vertex_color = "white", vertex_shape = "_",
                   vertex_size = vertex_size, aspect_ratio = "automatic", **kwargs)
    else:
        poset.show(label_elements= False, vertex_size = vertex_size,
                   aspect_ratio = "automatic", **kwargs)

def TorsLattice(data = None, *args, **kwargs):
    """
    Construct a lattice of torsion classes from various forms of input data

    This raises an error if the constructed lattice is not semidistributive,
    since the lattice of torsion classes is semidistributive.

    INPUT:

    - ``data``, ``*args``, ``**kwargs`` -- data and options that will
      be passed down to :func:`LatticePoset` to construct a poset that is
      also a lattice.

    OUTPUT:

    An instance of :class:`FiniteTorsLattice`

    """
    if isinstance(data, FiniteTorsLattice) and not args and not kwargs:
        return data
    L = LatticePoset(data, *args, **kwargs)
    if not L.is_semidistributive():
        raise ValueError("This lattice is not semidistributive.")
    return FiniteTorsLattice(L)

class FiniteTorsLattice(FiniteLatticePoset):
    """
    A subclass of :class:`FiniteLatticePoset`,
    which we regard as the class of lattices of all torsion classes
    of an abelian length category.
    The argument passed to FiniteTorsLattice is assumed to be
    a finite semidistributive lattice.
    """

    def _repr_(self):
        return "Lattice of torsion classes of some tau-tilting finite algebra having %s torsion classes" % self._hasse_diagram.order()

    @cached_method
    def zero(self):
        """
        Return the smallest torsion class $0$
        """
        return self.bottom()

    @cached_method
    def whole(self):
        """
        Return the largest torsion class, i.e. the whole abelian category
        """
        return self.top()

    @cached_method
    def all_itvs(self):
        """
        Return the set of all intervals in the torsion poset
        """
        return {(U,T) for U in self for T in self if self.is_lequal(U,T)}

    @cached_method
    def simples(self):
        """
        Return the set of simple torsion classes

        Here a simple torsion class is a Serre subcategory which contains
        exactly one simple module, or equivalently,
        torsion classes from which there are arrows to $0$.
        We can use this to represent the list of simple modules.
        """
        return set(self.upper_covers(self.zero()))

    @cached_method
    def all_bricks(self):
        """
        Return the set of all bricks represented by join-irreducibles

        We always use join-irreducible torsion classes
        to represent bricks by a bijection in [DIRRT].

        REFERENCES:

        .. [DIRRT] L. Demonet, O. Iyama, N. Reading, I. Reiten, H. Thomas,
           Lattice theory of torsion classes, arXiv:1711.01785.

        """
        return set(self.join_irreducibles())

    @cached_method
    def kappa(self, T):
        r"""
        Return the (extended) kappa map of ``T``

        This is computed as follows:
        Let $B_1,\dots, B_k$ be brick labels of all arrows starting from $T$.
        Then $T$ is the join of $T(B_1), \dots, T(B_k)$,
        where $T(B)$ is the smallest torsion classes containing $B$.
        The kappa map $\kappa(T)$ is defined to be the intersection of
        $^\perp B_1, \dots, {}^\perp B_k$.
        This operation maps the canonical join representation
        to the canonical meet representation.
        See [BTZ] for the detail.

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``

        OUTPUT:

        an element of ``self``

        REFERENCES:

        .. [BTZ] E. Barnard, G. Todorov, S. Zhu,
           Dynamical combinatorics and torsion classes,
           J. Pure Appl. Algebra 225 (2021), no. 9, 106642.
        """
        T = self(T) # Make sure that it is an element of `self`
        return _extended_kappa(self, T)

    @cached_method
    def bricks_in_tors(self, T):
        r"""
        Return the set of bricks contained in a torsion class ``T``

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``

        OUTPUT:

        the frozenset of bricks (represented by join-irreducibles in ``self``)
        contained in ``T``

        """
        T = self(T) # Make sure that it is an element of `self`
        return frozenset({j for j in self.all_bricks() if self.is_lequal(j,T)})

    @cached_method
    def bricks_in_torf(self, T):
        r"""
        Return the set of bricks contained in a torsion-free class $T^\perp$

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``

        OUTPUT:

        the frozenset of bricks (represented by join-irreducibles in ``self``)
        contained in the torsion-free class corresponding to ``T``,
        i.e. $T^\perp$
        """
        T = self(T) # Make sure that it is an element of `self`
        return frozenset(j for j in self.all_bricks()
                         if self.is_gequal(self.kappa(j),T) )

    @cached_method
    def bricks(self, itv, *, check = True):
        r"""
        Return the set of bricks in the heart of an interval of torsion classes

        For two torsion classes $U,T$ with $U \subseteq T$,
        its heart is $T \cap U^\perp$ (see [ES]).

        INPUT:

        - ``itv`` -- a pair (tuple) of torsion classes

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``itv`` is actually an interval

        OUTPUT:

        the frozenset of bricks (represented by join-irreducibles)
        contained in the heart of the given interval

        REFERENCES:

        .. [ES] H. Enomoto, A. Sakai,
           ICE-closed subcategories and wide $\tau$-tilting modules,
           to appear in Math. Z.
        """
        U, T = itv
        U, T = self(U), self(T) # Make sure that they are elements of `self`
        if check and not self.is_lequal(U,T):
            raise ValueError("This is not an interval.")
        return self.bricks_in_tors(T) & self.bricks_in_torf(U)

    @cached_method
    def label(self, itv, *, check = True):
        r"""
        Return the brick label of an Hasse arrow in the lattice of torsion classes

        For a Hasse arrow $T \to U$, its label is a unique brick
        contained in $T \cap U^\perp$ [DIRRT].

        INPUT:

        - ``itv`` -- a pair (tuple) of torsion classes (U,T),
          which we expect that U is covered by T

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``itv`` actually gives a covering relation

        REFERENCES:

        .. [DIRRT] L. Demonet, O. Iyama, N. Reading, I. Reiten, H. Thomas, Lattice theory of torsion classes, arXiv:1711.01785.
        """
        bricks_in = self.bricks(itv)
        if check and len(bricks_in) > 1:
            raise ValueError("The heart contains more than one brick, \
                             so not a covering relation.")
        return list(bricks_in)[0]

    @cached_method
    def plus(self, U):
        """
        Return the join of all Hasse arrows ending at ``U``

        For a torsion class $U$, its plus $U^{+}$ satisfies that
        $[U,U^{+}]$ is a wide interval which is the largest wide interval
        of the form $[U,T]$.

        INPUT:

        - ``U`` -- an element (torsion class) of ``self``
        """
        U = self(U) # Make sure that it is an element of `self`
        if U == self.whole():
            return U
        upper = self.upper_covers(U)
        return self.join(upper)

    @cached_method
    def minus(self, T):
        """
        Return the meet of all Hasse arrows starting at ``T``

        For a torsion class $T$, its minus $T^{-}$ satisfies that
        $[T^{-},T]$ is a wide interval which is the largest wide interval
        of the form $[U,T]$.

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``
        """
        T = self(T) # Make sure that it is an element of `self`
        if T == self.zero():
            return T
        lower = self.lower_covers(T)
        return self.meet(lower)

    def is_wide_itv(self, itv, *, check = True):
        r"""
        Return ``True`` if ``itv`` is a wide interval, and ``False`` otherwise

        An interval $[U,T]$ is a wide interval if its heart
        $T \cap U^\perp$ is a wide subcategory.
        This method uses a characterization of wide intervals
        given in [AP].

        INPUT:

        - ``itv`` -- a pair (tuple) of torsion classes,
          which is expected to be an interval

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``itv`` is actually an interval

        REFERENCES:

        .. [AP] S. Asai, C. Pfeifer,
           Wide subcategories and lattices of torsion classes,
           arXiv:1905.01148.
        """
        U, T = itv
        U, T = self(U), self(T) # Make sure that they are elements of `self`
        if check and not self.is_lequal(U,T):
            raise ValueError("This is not an interval.")
        if U == T:
            return True
        covers = [x for x in self.upper_covers(U) if self.is_lequal(x,T)]
        return T == self.join(covers)

    def is_ice_itv(self, itv, *, check = True):
        r"""
        Return ``True`` if ``itv`` is an ICE interval, and ``False`` otherwise

        An interval $[U,T]$ is a wide interval if its heart
        $T \cap U^\perp$ is an ICE-closed subcategory, that is,
        closed under taking images, cokernels, and extensions.
        This method uses a characterization of ICE intervals
        given in [ES].

        INPUT:

        - ``itv`` -- a pair (tuple) of torsion classes,
          which is expected to be an interval

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``itv`` is actually an interval

        REFERENCES:

        .. [ES] H. Enomoto, A. Sakai,
           ICE-closed subcategories and wide $\tau$-tilting modules,
           to appear in Math. Z.
        """
        U,T = itv
        U, T = self(U), self(T) # Make sure that they are elements of `self`
        if check and not self.is_lequal(U,T):
            raise ValueError("This is not an interval.")
        return self.is_lequal(T,self.plus(U))

    def is_ike_itv(self, itv, *, check = True):
        r"""
        Return ``True`` if ``itv`` is an IKE interval, and ``False`` otherwise

        An interval $[U,T]$ is a wide interval if its heart
        $T \cap U^\perp$ is an IKE-closed subcategory, that is,
        closed under taking images, kernels, and extensions.
        This function is just a dual of :func:`is_ice_itv`.

        INPUT:

        - ``itv`` -- a pair (tuple) of torsion classes,
          which is expected to be an interval

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``itv`` is actually an interval
        """
        U,T = itv
        U, T = self(U), self(T) # Make sure that they are elements of `self`
        if check and not self.is_lequal(U,T):
            raise ValueError("This is not an interval.")
        return self.is_lequal(self.minus(T),U)

    def itv_lequal(self, itv1, itv2):
        r"""
        Return whether the heart of ``itv1`` is contained in that of ``itv2``

        The heart of an interval $[U,T]$ is a subcategory $T \cap U^\perp$.
        By [DIRRT], the heart is recovered from bricks contained in it,
        hence this function compare the sets of bricks in two hearts.

        INPUT:

        - ``itv1``, ``itv2`` -- pairs (tuples) of torsion classes,
          which are assumed to be intervals

        OUTPUT:

        ``True`` if the heart of ``itv1`` is contained in that of ``itv2``,
        and ``False`` otherwise.
        """
        return set(self.bricks(itv1)).issubset(self.bricks(itv2))

    def wide_simples(self, itv):
        """
        Return the list of simple objects in a wide subcategory corresponding to ``itv``

        INPUT:

        - ``itv`` -- a pair (tuple) of torsion class, which we assume is a wide interval

        OUTPUT:

        the set of simple objects (bricks represented by join-irreducibles) of a wide subcategory which is the heart of ``itv``
        """
        U, T = itv
        U, T = self(U), self(T) # Make sure that they are elements of `self`
        if not self.is_wide_itv((U,T)):
            raise ValueError("This interval is not a wide interval.")

        covers = [x for x in self.upper_covers(U) if self.is_lequal(x,T)]
        return {self.label((U,x), check = False) for x in covers}

    def wide_lequal(self, U, T):
        r"""
        Compare two wide subcategories corresponding to two torsion classes

        If there are only finitely many torsion classes, then there is a bijection
        between the set of torsion classes and the set of wide subcategories
        by [MS] for finite-dimensional algebras and [E] for an abelian length category, see also [AP].
        Write $W_L(T)$ for the wide subcategory corresponding to $T$,
        which is a filtration closure of the brick labels of all Hasse arrows starting at $T$.
        Then the smallest torsion class containing $W_L(T)$ is $T$.
        This method returns whether $W_L(U) \subseteq W_L(T)$.

        INPUT:

        - ``U``, ``T`` -- elements of ``self`` (torsion classes)

        OUTPUT:

        ``True`` if $W_L(U)$ is contained in $W_L(T)$, and ``False`` otherwise

        REFERENCES:

        .. [MS] F. Marks, J. Stovicek,
           Torsion classes, wide subcategories and localisations,
           Bull. London Math. Soc. 49 (2017), Issue 3, 405–416.

        .. [E] H. Enomoto,
           Monobrick, a uniform approach to torsion-free classes and wide subcategories,
           arXiv:2005.01626.
        """
        U, T = self(U), self(T) # Make sure that they are elements of `self`
        kappa_U, kappa_T = self.kappa(U), self.kappa(T)
        return self.is_lequal(U, T) and self.is_gequal(kappa_U, kappa_T)

    def wide_lattice(self):
        """
        Return the lattice of wide subcategories

        The underlying set of this lattice is the same as ``self``, and
        its partial order is given by :meth:``wide_lequal``.

        OUTPUT:

        an instance of :class:`sage.combinat.posets.lattices.FiniteLatticePoset`
        """
        return LatticePoset((self, self.wide_lequal))

    def ice_lattice(self):
        """
        Return the lattice of ICE-closed subcategories, that is,
        subcategories closed under images, cokernels, and extensions.

        This lattice is realized as a poset of sets of bricks
        (represented by join-irreducibles) contained in ICE-closed subcategories.

        OUTPUT:

        an instance of :class:`sage.combinat.posets.lattices.FiniteLatticePoset`

        REFERENCES:

        .. [ES] H. Enomoto, A. Sakai,
           ICE-closed subcategories and wide $\tau$-tilting modules,
           to appear in Math. Z.
        """
        ice_bricks = {self.bricks(itv, check = False) for itv in self.all_itvs()
                      if self.is_ice_itv(itv, check = False)}
        return LatticePoset((ice_bricks, attrcall("issubset")))

    def ike_lattice(self):
        """
        Return the lattice of IKE-closed subcategories, that is,
        subcategories closed under images, kernels, and extensions.

        This lattice is realized as a poset of sets of bricks
        (represented by join-irreducibles) contained in IKE-closed subcategories.

        OUTPUT:

        an instance of :class:`sage.combinat.posets.lattices.FiniteLatticePoset`
        """
        ike_bricks = {self.bricks(itv, check = False) for itv in self.all_itvs()
                      if self.is_ike_itv(itv, check = False)}
        return LatticePoset((ike_bricks, attrcall("issubset")))

    def heart_poset(self):
        """
        Return the poset of torsion hearts ordered by inclusion

        A torsion heart is a subcategory which arises as a heart of some interval
        of torsion classes. For example, every wide subcategory, ICE-closed subcategory is
        a torsion heart.
        This poset is not a lattice in general.

        This poset is realized as a poset of sets of bricks
        (represented by join-irreducibles) contained in torsion hearts.

        OUTPUT:

        an instance of :class:`sage.combinat.posets.posets.FinitePoset`
        """
        brick_set = {self.bricks(itv, check = False) for itv in self.all_itvs()}
        return Poset((brick_set, attrcall("issubset")))

    def indec_tau_rigid(self):
        r"""
        Return the set of indecomposable $\tau$-rigid modules,
        represented by join-irreducible torsion classes.

        For a $\tau$-tilting finite algebra, there is a bijection by [DIJ] between
        indecomposable $\tau$-rigid modules and join-irreducible torsion classes.
        The correspondence is $T(M) = \mathsf{Fac} M$ for a $\tau$-rigid $M$, and
        the unique indecomposable split projective object in $T$
        for a join-irreducible torsion class $T$.

        Since this is the same as :meth:`all_bricks`,
        this function is only needed for the readability reason.

        REFERENCES:

        .. [DIJ] L. Demonet, O. Iyama, G. Jasso,
           $\tau$-tilting finite algebras, bricks, and g-vectors,
           Int. Math. Res. Not. IMRN 3, 852--892 (2019).
        """
        return self.all_bricks()

    @cached_method
    def has_tau_rigid_summand(self, M, *, check = True):
        r"""
        Return the set of $\tau$-tilting pairs which has ``M`` as a $\tau$-rigid summand

        We consider ``self`` as the set of support $\tau$-tilting pairs.
        Then this returns the set of support $\tau$-tilting pairs
        which contain $(M,0)$ as a direct summand.
        We use join-irreducible torsion classes to represent indecomposable $\tau$-rigid modules.
        See :meth:`indec_tau_rigid`.

        INPUT:

        - ``M`` -- an element of ``self``, which is expected to be join-irreducible

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``M`` is actually join-irreducible
        """
        M = self(M) # Make sure that it is an element of `self`
        if check and M not in self.indec_tau_rigid():
            raise ValueError("This is not join-irreducible.")
        M_plus = self.plus(M)
        # then [M, M_plus] is the set of tau-tilting pairs
        # containing (M,0) as a summand.
        return {T for T in self if self.is_lequal(M,T) and self.is_lequal(T,M_plus) }

    @cached_method
    def has_support_summand(self, S, *, check = True):
        r"""
        Return the set of $\tau$-tilting pairs which have the projective cover of ``S`` as a support summand

        We consider ``self`` as the set of support $\tau$-tilting pairs.
        Then this returns the set of support $\tau$-tilting pairs
        which contain $(0,P)$ as a direct summand,
        where $P$ is the projective cover of a simple module ``S``.
        We use simple torsion classes to represent a simple module,
        hence ``S`` is expected to be a simple torsion class, that is,
        a Serre subcategory with one simple module.

        INPUT:

        - ``S`` -- an element of ``self``, which is expected to be a simple torsion class

        - ``check`` -- a Boolean (default: ``True``),
          whether to check ``S`` is actually a simple torsion class
        """
        S = self(S) # Make sure that it is an element of `self`
        if check and S not in self.simples():
            raise ValueError("This is not a simple torsion class (doesn't cover 0).")
        # We compute the Serre subcategory ``non_S_Serre`` consisting of modules
        # such that ``S`` don't appear as composition factors.
        non_S_simple = set(self.simples()) - {S}
        non_S_Serre = self.join(non_S_simple)
        # Then a $\tau$-tilting pair contains $(0,P)$ as a summand
        # if there's no non-zero map from P to any element in the corresponding torsion class $T$,
        # that is, $T$ is contained in ``non_S_Serre``.
        return {T for T in self if self.is_lequal(T,non_S_Serre)}

    def projectives(self, T):
        r"""
        Return the set of indecomposable Ext-projectives of ``T`` represented by
        join-irreducibles

        We use join-irreducible torsion classes to represent indecomposable $\tau$-rigid
        modules, see :meth:``indec_tau_rigid``.

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``
        """
        T = self(T) # Make sure that it is an element of `self`
        return {M for M in self.indec_tau_rigid()
                if T in self.has_tau_rigid_summand(M, check = False)}

    def composition_factors(self, T):
        r"""
        Return the set of composition factors of all modules in ``T``

        We use simple torsion classes to represent simple modules,
        see :meth:``simples``.

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``
        """
        T = self(T) # Make sure that it is an element of `self`
        return {S for S in self.simples() if T not in self.has_support_summand(S, check = False)}

    def is_sincere(self, T):
        r"""
        Return ``True`` if ``T`` is a sincere torsion class and ``False`` otherwise

        INPUT:

        - ``T`` -- an element (torsion class) of ``self``
        """
        T = self(T) # Make sure that it is an element of `self`
        return len(self.composition_factors(T)) == len(self.simples())

    def tau_rigid_pair_summand(self, T):
        r"""
        Return the set of indecomposable $\tau$-rigid pairs which are direct summands of ``T``

        We represent indecomposable $\tau$-rigid pairs as follows.
        - For a pair $(M,0)$ with $M$ being indecomposable $\tau$-rigid,
          we use ``(M,0)`` for ``M`` in ``self.indec_tau_rigid()``,
          that is, ``M`` is the join-irreducible torsion class corresponding to $M$.
        - For a pair $(0,P)$ with $P$ being indecomposable projective,
          we use ``(S,1)``, where ``S`` is a simple module $\mathrm{top} P$
          represented by the simple torsion class.

        INPUT:

        - ``T`` -- an element of ``self`` considered as a $\tau$-tilting pair
        """
        T = self(T) # Make sure that it is an element of `self`
        return {(M,0) for M in self.projectives(T)} | \
               {(S,1) for S in self.simples()
                if T in self.has_support_summand(S, check = False)}

    def s_tau_tilt_complex(self):
        r"""
        Return the support $\tau$-tilting simplicial complex of the algebra

        This is a simplicial complex whose simplices are $\tau$-rigid pairs.
        This is the same as a simplicial complex of 2-term silting complexes, called $\Delta(A)$ in [DIJ].
        There are some papers studying this simplicial complex, e.g. [AMN].

        OUTPUT:

        an instance of :class:`sage.homology.simplicial_complex.SimplicialComplex`

        REFERENCES:

        .. [DIJ] L. Demonet, O. Iyama, G. Jasso,
           $\tau$-tilting finite algebras, bricks, and g-vectors,
           Int. Math. Res. Not. IMRN 3, 852--892 (2019).

        .. [AMN] H. Asashiba, Y. Mizuno, K. Nakashima,
           Simplicial complexes and tilting theory for Brauer tree algebras,
           J. Algebra 551 (2020), 119--153.
        """
        return SimplicialComplex([self.tau_rigid_pair_summand(T) for T in self],
                                 maximality_check = False)

    def positive_tau_tilt_complex(self):
        r"""
        Return the positive $\tau$-tilting simplicial complex of the algebra

        This is a full subcomplex of the support $\tau$-tilting complex
        consisting of $\tau$-tilting modules, that is, $\tau$-tilting pairs of
        the form $(M,0)$. See [G] for example.
        Historically, this is a simplicial complex associated with tilting modules
        studied by [RS] and [U] for the hereditary case.

        OUTPUT:

        an instance of :class:`sage.homology.simplicial_complex.SimplicialComplex`

        REFERENCES:

        .. [G] Y. Gyoda,
           Positive cluster complexes and $\tau$-tilting simplicial complexes
           of cluster-tilted algebras of finite type,
           arXiv:2105.07974

        .. [RS] C. Riedtmann and A. Schofield,
           On a simplicial complex associated with tilting modules,
           Comment. Math. Helv. 66 (1991), no. 1, 70--78.

        .. [U] L. Unger,
           Shellability of simplicial complexes arising in representation theory,
           Adv. Math. 144 (1999), no. 2, 221--246.
        """
        return SimplicialComplex([self.projectives(T) for T in self if self.is_sincere(T)],
                                 maximality_check = False)


    def number_of_projs(self, arg):
        r"""
        Return the number of indecomposable Ext-projective objects in a given subcategory

        If ``arg`` is an element of ``self`` (i.e. a torsion class),
        then the considered category is ``arg`` itself.
        If ``arg`` is an interval $[U, T]$ of torsion classes, then this considers
        the heart of this interval, i.e. $T \cap U^\perp$.
        This is based on [ES, Corollary 4.28]

        INPUT:

        - ``arg`` -- either an element of ``self``, or an interval  in ``self`` as a tuple

        REFERENCES:

        .. [ES] H. Enomoto, A. Sakai,
           ICE-closed subcategories and wide $\tau$-tilting modules,
           to appear in Math. Z.
        """
        if isinstance(arg, tuple):
            U, T = arg
        else:
            U, T = self.zero(), arg
        U, T = self(U), self(T) # Make sure that they are elements of `self`

        T_minus_U = {M for M in self.projectives(T) if not self.is_lequal(M,U)}
        return len(T_minus_U)
