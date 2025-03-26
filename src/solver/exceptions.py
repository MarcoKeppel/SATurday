"""
    This module contains the exceptions that can be raised by the solver.
"""

# NOTE//XXX: should probably return a status obj instead of raising exceptions
#            e.g. return SolverStatus(UNSAT, core=core) or SolverStatus(SAT, model=model), ...
# NOTE: related to the above, could also not include the core but instead have a method to get the core
#       from the main CDCL loop method. Same goes for the (possibly partial) model (the model is already
#       stored in the implication graph, no need to make new methods)
class UnsatException(Exception):
    def __init__(self, reason):
        self.reason = reason    # TODO: typing
    
    def __str__(self):
        return f"UNSAT: {self.conflict_clause}"

    def __repr__(self):
        return self.__str__()
