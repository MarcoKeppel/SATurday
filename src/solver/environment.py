import logging
from collections import defaultdict
from itertools import chain

from src.datastructs.formula import *

"""
    This module contains the SolverEnvironment class, which is responsible for
    managing the state of the solver.
"""

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG) 

class StepParent:
    """
        A parent of a solver step
    """
    def __init__(self, lit: ClauseLiteral, clause: Clause):
        self.literal = lit
        self.clause = clause

    def __str__(self):
        return f"StepParents({self.parents})"

class SolverStep:
    """
        A step in the solver stack
    """
    def __init__(self, lit: ClauseLiteral, parents: list[StepParent]):
        self.parents = parents
        self.parents_map = { parent.literal.variable: parent for parent in parents }
        self.literal = lit

    def get_parents(self):
        return self.parents

    def is_decision(self):
        raise NotImplementedError
    
    def is_unit(self):
        raise NotImplementedError

    def __str__(self):
        return f"SolverStep({self.variable}, {self.value})"

class UnitPropagationStep(SolverStep):
    """
        A unit propagation step
    """
    def __init__(self, lit: ClauseLiteral, antecedent_clause: Clause, parents: list[StepParent]):
        super().__init__(lit, parents)
        self.antecedent_clause = antecedent_clause

    def is_decision(self):
        return False

    def is_unit(self):
        return True

    def get_antecedent_clause(self):
        return self.antecedent_clause

    def __str__(self):
        return f"UnitPropagationStep({self.clause}, {self.literal})"

class DecisionStep(SolverStep):
    """
        A decision step
    """
    def __init__(self, lit: ClauseLiteral):
        super().__init__(lit, [])

    def is_decision(self):
        return True

    def is_unit(self):
        return False

    def __str__(self):
        return f"DecisionStep({self.variable}, {self.value})"

class ImplicationGraph:
    """
        The implication graph built by the solver
    """
    def __init__(self):
        # self.nodes: dict[Literal] = dict()
        # self.edges: dict[(Literal, Literal), Clause] = dict()
        self.level = 0
        # self.stack: list[Literal] = [ ]
        self.stack: list[SolverStep] = [ ]
        self.lits_map: dict[BooleanVariable, SolverStep] = dict()

    def is_consistent(self):
        return not any(self.is_conflict(lit) for lit in self.nodes)

    def add_decision(self, lit: ClauseLiteral):
        """
            Adds a node to the implication graph
        """
        # if not self.is_conflict(lit):
        if True:
            node = DecisionStep(lit)
            self._add_node(node)
        else:
            # TODO: custon exception
            # TODO: provide more info in exception message
            raise Exception("Conflict detected")

    # def add_unit(self, lit: ClauseLiteral, parents: dict[ClauseLiteral, Clause] = None):
    def add_unit(self, lit: ClauseLiteral, antecedent_clause: Clause):
        """
            Adds a node to the implication graph
        """
        # if not self.is_conflict(lit):
        if True:
            parents = [ ]
            for p_lit in antecedent_clause.get_literals():
                # NOTE: can the same objects as in the clause be used here?
                parents.append(StepParent(p_lit, antecedent_clause))
            node = UnitPropagationStep(lit, antecedent_clause, parents)
            self._add_node(node)
        else:
            # TODO: custon exception
            # TODO: provide more info in exception message
            raise Exception("Conflict detected")

    def _add_node(self, node: SolverStep):
        self.stack.append(node)
        self.lits_map[node.literal.variable] = node

    def get_last_decision(self) -> SolverStep:
        for node in reversed(self.stack):
            if node.is_decision():
                return node
        return None

    def get_last_step(self) -> SolverStep:
        return self.stack[-1]

    def pop(self) -> SolverStep:
        res = self.stack.pop()
        del self.lits_map[res.literal.variable]
        return res

    def pop_until_decision(self) -> Iterable[SolverStep]:
        while not self.is_decision(self.stack[-1]):
            res = self.stack.pop()
            del self.lits_map[res.literal.variable]
            yield res
        es = self.stack.pop()
        del self.lits_map[res.literal.variable]
        yield res

    def add_edge(self, parent: Literal, child: Literal, clause: Clause):
        """
            Adds an edge to the implication graph
        """
        # self.edges[(parent, child)] = clause
        if parent not in self.nodes[child]:
            self.nodes[child][parent] = clause

    def get_parents(self, lit: Literal):
        """
            Returns the parents of a literal
        """
        return self.nodes[lit]

    def get_model(self) -> Iterable[Literal]:
        """
            Returns the (partial) model of the implication graph
        """
        return [ node.literal for node in self.stack ]

    def get_model_map(self) -> dict[BooleanVariable, bool]:
        """
            Returns the (partial) model of the implication graph as a dict
        """
        return { node.literal.variable: node.literal.polarity for node in self.stack }

    def is_decision(self, lit: Literal):
        """
            Returns whether a literal is a decision
        """
        # TODO: handle case where lit is not in self.nodes
        # return self.parents[lit] == []
        return not self.nodes[lit]

    def __contains__(self, lit: Literal):
        raise NotImplementedError

    def __str__(self):
        return f"ImplicationGraph({self.nodes})"
    
    def __repr__(self):
        return self.__str__()


class SolverEnvironment:
    """
        The solver environment, which manages the state of the solver
    """
    def __init__(self):
        self.variables: list[BooleanVariable] = [ ]
        self.clauses: list[Clause] = [ ]
        self.learned_clauses: list[Clause] = [ ]
        self.variables_occurrences: dict[BooleanVariable, int] = defaultdict(lambda: 0)
        # self.model_map: dict[Literal, SolverStep] = dict()
        # self.stack: dict[BooleanVariable, SolverStep] = dict()
        # self.current_decision_step: DecisionStep = DecisionStep(None, None)
        self.implication_graph: ImplicationGraph = ImplicationGraph()

    def add_clause(self, clause: Clause):
        """
            Adds a clause to the solver environment
        """
        self.clauses.append(clause)
        # NOTE: O(n^2) !
        self.variables.update({var for var in clause.variables() if var not in self.variables})
        for var in clause.variables():
            self.variables_occurrences[var] += 1
    
    def unit_propagate_literal(self, clause: Clause, lit: Literal):
        """
            Performs unit propagation for a literal
        """
        if lit in clause:
            clause[lit] = True

    def unit_propagate_clause(self, clause: Clause):
        """
            Performs unit propagation for a clause
        """
        lit = clause.get_unit()
        for c in self.clauses:
            self.unit_propagate_literal(c, lit)

    def unit_propagate(self):
        """
            Performs unit propagation
        """

        propagation = True  
        while propagation:
            propagation = False

            # Find unit clause (if any)
            unit_clause: Clause = None
            unit_lit: ClauseLiteral = None
            model_map = self.implication_graph.get_model_map()
            for c in self.clauses:
                if c.is_unit(model_map):
                    propagation = True
                    unit_clause = c
                    unit_lit = c.get_unit(model_map)
                    _logger.debug(f"Clause { c } is unit: deduced { unit_lit }")
                    break
            # No unit clauses found
            if unit_clause is None:
                _logger.debug("No unit clauses found")
                return None

            assert unit_clause and unit_lit

            # Perform unit propagation
            print(self.implication_graph.get_model())
            self.implication_graph.add_unit(unit_lit, unit_clause)
            print(f"added {unit_lit}")
            print(self.implication_graph.get_model())
            model_map = self.implication_graph.get_model_map()

            # Check for conflicts
            conflict_clause: Clause = None
            for c in self.clauses:
                if not c.is_consistent(model_map):
                    conflict_clause = c
                    _logger.debug(f"Conflict detected with clause { c }")
                    break
                else:
                    pass
                    # _logger.debug(f"Clause { c } is consistent")
            
            # If no conflict, continue
            if conflict_clause is None:
                _logger.debug(f"Partial model { self.implication_graph.get_model() } {self.implication_graph.get_model_map() } is consistent")
                continue

            # Perform conflict analysis
            self.conflict_analysis(conflict_clause)

    def conflict_analysis(self, conflict_clause: Clause):
        """
            Performs conflict analysis with resolution
        """
        _logger.debug(f"Performing conflict analysis with conflict clause { conflict_clause }")

        learned_clause = conflict_clause

        # Use 'decision' criterion
        while not self.implication_graph.get_last_step().is_decision():
            # Resolve with antecedent
            # TODO: make method for this
            prev_step = self.implication_graph.pop()
            antecedent_clause = prev_step.get_antecedent_clause()
            _logger.debug(f"Resolving with antecedent clause { antecedent_clause }")
            lits = set(chain(learned_clause.get_literals(), antecedent_clause.get_literals()))
            learned_clause = Clause([ lit for lit in lits if ClauseLiteral(lit.variable, not lit.polarity) not in lits ], f"l{ len(self.learned_clauses) }")
            _logger.debug(f"Resolved: { learned_clause }")

        self.clauses.append(learned_clause)
        self.learned_clauses.append(learned_clause)

        _logger.debug(f"Learned clause: { learned_clause }")

        # Backjump ("original strategy" by J. P. M. Silva and K. A. Sakallah. in 'GRASP - A new Search Algorithm for Satisfiability')
        # Reach decision
        while not self.implication_graph.get_last_step().is_decision():
            self.implication_graph.pop()
        # Pop decision
        self.implication_graph.pop()

        _logger.debug(f"Backjumped to partial model { self.implication_graph.get_model() }")
        
        # NOTE: let unit propagation be done by the caller
        # # Unit propagate learned clause
        # unit_lit = learned_clause.get_unit(self.implication_graph.get_model_map())
        # self.implication_graph.add_unit(unit_lit, unit_clause)

    def cdcl(self):
        """
            Performs the Conflict-Driven Clause Learning algorithm
        """

        _logger.debug("Clauses:")
        for c in self.clauses:
            _logger.debug(f"  - { c }")

        _logger.debug("= "*32)
        _logger.debug("Starting CDCL algorithm")
        _logger.debug("= "*32)

        # HACK:

        try:
            while True:
                # Deterministic choices

                conflict = self.unit_propagate()

                if conflict is not None:
                    _logger.debug(f"Conflict detected with clause { conflict }")
                
                # Non-deterministic choices

                # HACK: get first var not yet assigned, set if to false, add it to the implication graph
                # var = next(var for var in self.variables if var not in self.implication_graph)
                var = next(var for var in self.variables if var not in self.implication_graph.lits_map)
                _logger.debug(f"Next decision: { var } = False")
                # self.implication_graph.add_node(NotLiteral(var))
                self.implication_graph.add_decision(ClauseLiteral(var, False))
        except StopIteration:
            pass
        
        _logger.debug("= "*32)
        _logger.debug("CDCL algorithm finished")
        _logger.debug(f"Model: { self.implication_graph.get_model() }")

    def __str__(self):
        return f"SolverEnvironment(\n  variables: {self.variables},\n  clauses: {self.clauses}\n)"
