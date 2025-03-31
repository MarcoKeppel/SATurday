from src.datastructs.formula import *

# HACK: quick and dirty implementation
def parse_dimacs(file_path: str) -> tuple[list[BooleanVariable], list[Clause]]:

    with open(file_path, "r") as file:
        lines = file.readlines()
        # Remove comments:
        lines = [l for l in lines if not l.startswith("c")]
        # Read header:
        header = lines[0].split()
        assert header[0] == "p"
        assert header[1] == "cnf"
        num_vars = int(header[2])
        # NOTE: do not be strict about the number of clauses
        num_clauses = int(header[3])

        # Create variables:
        variables = [BooleanVariable(f"v{i}") for i in range(1, num_vars + 1)]

        # Read clauses:
        clauses = []
        for l in lines[1:]:
            clause = []
            for lit in l.split():
                if lit == "0":
                    break
                lit = int(lit)
                var = variables[abs(lit) - 1]
                clause.append(ClauseLiteral(var, lit > 0))
            clauses.append(Clause(clause))

        return variables, clauses
