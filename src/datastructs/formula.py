from typing import Iterable

"""
    This module contains classes to represent formulas (input formulas, solver clauses, ...)
"""

class FormulaNode:
    """
        A generic node in the formula tree/DAG
    """
    def __init__(self, children: Iterable['FormulaNode']):
        self.children = children
    
    def __str__(self):
        raise NotImplementedError()
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        # NOTE: purely syntactic equality, not semantic:
        #   - does not consider commutative properties (operators can override it to do so)
        #   - ...
        return type(self) == type(other) and self.children == other.children

class BooleanOperator(FormulaNode):
    """
        A generic boolean operator (e.g. AND, OR, NOT, ...)
    """
    def __init__(self, children: Iterable['FormulaNode']):
        super().__init__(children)

class And(BooleanOperator):
    """
        Logical AND operator
    """
    def __str__(self):
        return f"( { ' AND '.join(str(child) for child in self.children) } )"
    
class Or(BooleanOperator):
    """
        Logical OR operator
    """
    def __str__(self):
        return f"( { ' OR '.join(str(child) for child in self.children) } )"

class Not(BooleanOperator):
    """
        Logical NOT operator
    """
    def __str__(self):
        return "! " + str(self.children[0])

class Clause(FormulaNode):
    """
        A clause (disjunction of literals)
    """
    def __init__(self, children: Iterable['FormulaNode']):
        super().__init__(children)
    def __str__(self):
        return f"( { ' OR '.join(str(child) for child in self.children) } )"

class Literal(FormulaNode):
    """
        A generic literal (e.g. an atom, a negated atom, ...)
    """
    def __init__(self, children: 'Literal'):
        super().__init__(children)


class Atom(Literal):
    """
        A generic atom (e.g. a predicate, a function, ...)
    """
    def __init__(self, children: 'Atom'):
        super().__init__(children)

class NotLiteral(Literal):
    """
        A negated atom
    """
    def __init__(self, children: Literal):
        super().__init__([children])
    
    def __str__(self):
        return "!" + str(self.children[0])

class BooleanConstant(Atom):
    """
        A boolean constant (True/False)
    """
    def __init__(self, value: bool):
        super().__init__([])
        self.value = value
    
    def __str__(self):
        return str(self.value)

class BooleanVariable(Atom):
    """
        A boolean variable (e.g. x1, x2, ...)
    """
    def __init__(self, name: str):
        super().__init__([])
        self.name = name
    
    def __str__(self):
        return self.name

class Clause(FormulaNode):
    """
        A clause (disjunction of literals)
    """
    def __init__(self, children: Iterable['Literal']):
        super().__init__(children)
        self.lits_interpretation: dict[Literal, bool] = { lit: None for lit in children }
    
    def get_lits(self) -> Iterable[Literal]:
        return self.children

    def __contains__(self, lit: Literal):
        return lit in self.lits_interpretation.keys()

    def __setitem__(self, lit: Literal, value: bool):
        try:
            self.lits_interpretation[lit] = value
        except KeyError as e:
            raise KeyError(f"Literal '{ lit }' not in clause { self }") from e

    def __getitem__(self, lit: Literal) -> bool:
        try:
            return self.lits_interpretation[lit]
        except KeyError as e:
            raise KeyError(f"Literal '{ lit }' not in clause { self }") from e

    def uninterpreted_lits(self) -> Iterable[Literal]:
        return (lit for lit, value in self.lits_interpretation.items() if value is None)

    def uninterpreted_lits_count(self) -> int:
        return sum(1 for lit in self.uninterpreted_lits())
    
    def has_interpretation(self, lit: Literal) -> bool:
        try:
            return self.lits_interpretation[lit] is not None
        except KeyError as e:
            raise KeyError(f"Literal '{ lit }' not in clause { self }") from e

    def __str__(self):
        return f"( { ' OR '.join(str(child) for child in self.children) } )"
