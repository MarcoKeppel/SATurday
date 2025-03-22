from typing import Iterable

"""
    This module contains classes to represent formulas (input formulas, solver clauses, ...)
"""

class FormulaNode:
    """
        A generic node in the formula tree/DAG
    """
    
    def __eq__(self, other):
        # NOTE: purely syntactic equality, not semantic:
        #   - does not consider commutative properties (operators can override it to do so)
        #   - ...
        return type(self) == type(other) and self.children == other.children

    def __str__(self):
        raise NotImplementedError()
    
    def __repr__(self):
        return str(self)

class NAryNode(FormulaNode):
    """
        A generic n-ary node in the formula tree/DAG
    """
    def __init__(self, children: Iterable['FormulaNode']):
        self.children = children
    
    def __eq__(self, other):
        # NOTE: purely syntactic equality, not semantic:
        #   - does not consider commutative properties (operators can override it to do so)
        #   - ...
        return type(self) == type(other) and self.children == other.children

    def __str__(self):
        raise NotImplementedError()
    
    def __repr__(self):
        return str(self)

class BooleanOperator(NAryNode):
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

    def __repr__(self):
        return self.__str__()
    
class Or(BooleanOperator):
    """
        Logical OR operator
    """
    def __str__(self):
        return f"( { ' OR '.join(str(child) for child in self.children) } )"
    
    def __repr__(self):
        return self.__str__()

class Not(BooleanOperator):
    """
        Logical NOT operator
    """
    def __str__(self):
        return "! " + str(self.children[0])
    
    def __repr__(self):
        return self.__str__()

class Literal(FormulaNode):
    """
        A generic literal (e.g. an atom, a negated atom, ...)
    """

class Atom(Literal):
    """
        A generic atom (e.g. a predicate, a function, ...)
    """

class BooleanConstant(Atom):
    """
        A boolean constant (True/False)
    """
    def __init__(self, value: bool):
        super().__init__([])
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()

class BooleanVariable(Atom):
    """
        A boolean variable (e.g. x1, x2, ...)
    """
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def invert(self) -> Literal:
        return NotLiteral(self)

    def __eq__(self, other):
        return isinstance(other, BooleanVariable) and self.name == other.name

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

class NotLiteral(Literal):
    """
        A negated atom
    """
    def __init__(self, variable: BooleanVariable):
        # TODO?: delete pairs of nested NotLiteral nodes
        super().__init__([variable])

    def get_variable(self) -> BooleanVariable:
        return self.children[0]

    def invert(self) -> Literal:
        return self.get_variable()
    
    def __hash__(self):
        return self.get_variable().name.__hash__() + 1 # XXX: ???

    def __str__(self):
        return "!" + str(self.children[0])

    def __repr__(self):
        return self.__str__()

class ClauseLiteral(Literal):

    def __init__(self, variable: BooleanVariable, polarity: bool):
        super().__init__()
        self.variable = variable
        self.polarity = polarity

    def __eq__(self, other):
        return isinstance(other, ClauseLiteral) and self.variable == other.variable and self.polarity == other.polarity

    def __hash__(self):
        return hash((self.variable, self.polarity))

    def __str__(self):
        return f"{ '' if self.polarity else '!' }{ self.variable }"

    def __repr__(self):
        return self.__str__()

class Clause(NAryNode):
    """
        A clause (disjunction of literals)
    """
    def __init__(self, children: Iterable['ClauseLiteral'], name: str | None = None):
        super().__init__(children)
        self.lits_polarity_map = { lit.variable: lit.polarity for lit in children }
        self.lits_map = { lit.variable: lit for lit in children }
        self.name = name

    def __contains__(self, variable: BooleanVariable):
        # return variable in self.children or NotLiteral(variable) in self.children
        return variable in self.get_lits_polarity()

    # def __setitem__(self, lit: Literal, value: bool):
    #     try:
    #         self.variables_interpretation[lit] = value
    #     except KeyError as e:
    #         raise KeyError(f"Literal '{ lit }' not in clause { self }") from e

    # def __setitem__(self, variable: BooleanVariable, value: bool):
    #     # try:
    #     #     self.variables_interpretation[variable] = value
    #     # except KeyError as e:
    #     #     raise KeyError(f"Variable '{ variable }' not in clause { self }") from e
    #     if variable in self.variables_interpretation:
    #         self.variables_interpretation[variable] = value
    #     else:
    #         raise KeyError(f"Variable '{ variable }' not in clause { self }")

    # def __getitem__(self, variable: BooleanVariable) -> bool:
    #     # return self.variables_interpretation[variable]
    #     try:
    #         return self.variables_interpretation[variable]
    #     except KeyError as e:
    #         raise KeyError(f"Variable '{ variable }' not in clause { self }") from e

    # def get_variables(self) -> Iterable[BooleanVariable]:
    #     return self.variables_interpretation.keys()

    # def uninterpreted_vars(self) -> Iterable[Literal]:
    #     return (variable for variable, value in self.variables_interpretation.items() if value is None)

    # def uninterpreted_vars_count(self) -> int:
    #     # NOTE: this or len(list(self.uninterpreted_vars()))?
    #     return sum(1 for var in self.uninterpreted_vars())
    
    # def is_unit(self) -> bool:
    #     if self.uninterpreted_vars_count() != 1: return False
    #     return all(interpretation == isinstance(variable, NotLiteral) for variable, interpretation in self.variables_interpretation.items() if interpretation is not None)

    # def is_consistent(self) -> bool:
    #     if self.uninterpreted_vars_count() > 0: return True
    #     return any(interpretation != isinstance(variable, NotLiteral) for variable, interpretation in self.variables_interpretation.items() if interpretation is not None)

    # def get_unit(self) -> tuple[BooleanVariable, bool]:
    #     if not self.is_unit():
    #         raise ValueError(f"Clause '{ self }' is not unit")
    #     var = next(self.uninterpreted_vars())
    #     return var, not isinstance(var, NotLiteral)

    # def has_interpretation(self, variable: BooleanVariable) -> bool:
    #     try:
    #         return self.variables_interpretation[variable] is not None
    #     except KeyError as e:
    #         raise ValueError(f"Variable '{ variable }' not in clause { self }") from e

    # def get_unassigned_vars(self, model: dict[BooleanVariable, bool]) -> list[BooleanVariable]:
    #     unassigned = [ ]
    #     for lit in self.get_lits():
    #         var = lit.get_variable() if isinstance(lit, NotLiteral) else lit
    #         if var not in model:
    #             unassigned.append(var)
    #     return unassigned

    def get_literals(self) -> list[ClauseLiteral]:
        return self.children

    def get_literal(self, variable: BooleanVariable) -> ClauseLiteral:
        return self.lits_map[variable]

    def get_literals_polarity_map(self) -> dict[BooleanVariable, bool]:
        return self.lits_polarity_map

    def get_unassigned_lits_map(self, model: dict[BooleanVariable, bool]) -> dict[BooleanVariable, bool]:
        return { var: polarity for var, polarity in self.get_literals_polarity_map().items() if var not in model }

    # def is_consistent(self, model: Iterable[ClauseLiteral]) -> bool:
    def is_consistent(self, model: dict[BooleanVariable, bool]) -> bool:
        for var, polarity in self.get_literals_polarity_map().items():
            # Unassigned lit, ok:
            if var not in model:
                return True
            # True lit, ok:
            elif model[var] == polarity:
                return True
        # Inconsistent:
        return False

    # def is_unit(self, model: Iterable[ClauseLiteral]) -> bool:
    def is_unit(self, model: dict[BooleanVariable, bool]) -> bool:
        n_unassigned = 0
        for var, polarity in self.get_literals_polarity_map().items():
            # Unassigned literal, increase counter:
            if var not in model:
                n_unassigned += 1
                # NOTE: could return early if n_unassigned > 1
            # False literal, ok:
            elif model[var] != polarity:
                pass
            # True literal, not unit:
            else:
                return False
        return n_unassigned == 1

    # def get_unit(self, model: Iterable[ClauseLiteral]) -> tuple[BooleanVariable, bool]:
    # def get_unit(self, model: Iterable[ClauseLiteral]) -> ClauseLiteral:
    def get_unit(self, model: dict[BooleanVariable, bool]) -> ClauseLiteral:
        if not self.is_unit(model):
            # TODO: custom exception
            # TODO: more info in exception message
            raise Exception("Clause is not unit")
        # At this point, it is guaranteed that there is exactly one unassigned literal.
        # Find it and return it imeediately.
        for var, polarity in self.get_literals_polarity_map().items():
            # Unassigned literal:
            if var not in model:
                # NOTE: return ClauseLiteral or tuple[BooleanVariable, bool] ?
                return self.get_literal(var)

    def __str__(self):
        return f"{ self.name or '' }{ ': ' if self.name else '' }( { ' OR '.join(str(child) for child in self.children) } )"

    def __repr__(self):
        return self.__str__()
