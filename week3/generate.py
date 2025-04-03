import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            # Create a copy to avoid modifying while iterating
            words_to_remove = set()
            for word in self.domains[var]:
                # If word length doesn't match variable length, remove it
                if len(word) != var.length:
                    words_to_remove.add(word)
            
            # Remove words of incorrect length
            self.domains[var] -= words_to_remove

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False
        overlap = self.crossword.overlaps[x, y]
        
        # If there's no overlap, x and y don't constrain each other
        if overlap is None:
            return False
        
        # Get the overlap positions
        i, j = overlap  # i is the position in x, j is the position in y
        
        # Check each word in x's domain
        words_to_remove = set()
        for x_word in self.domains[x]:
            # Check if there's any word in y's domain that satisfies the constraint
            if not any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                words_to_remove.add(x_word)
                revision_made = True
        
        # Remove incompatible words from x's domain
        self.domains[x] -= words_to_remove
        
        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initialize queue of arcs to process
        if arcs is None:
            queue = [(x, y) for x in self.crossword.variables 
                    for y in self.crossword.neighbors(x)]
        else:
            queue = list(arcs)
        
        # Process all arcs in the queue
        while queue:
            x, y = queue.pop(0)
            
            # If we revise the domain of x, need to check all of x's neighbors again
            if self.revise(x, y):
                # If x's domain is empty, this problem is unsolvable
                if not self.domains[x]:
                    return False
                
                # Add arcs for all of x's neighbors (except y)
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all(var in assignment for var in self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all values are distinct
        values = list(assignment.values())
        if len(values) != len(set(values)):
            return False
        
        # Check if all words have the correct lengths
        for var, word in assignment.items():
            if len(word) != var.length:
                return False
        
        # Check if all overlaps are consistent
        for var1 in assignment:
            for var2 in assignment:
                if var1 != var2:
                    overlap = self.crossword.overlaps[var1, var2]
                    if overlap:
                        i, j = overlap
                        if assignment[var1][i] != assignment[var2][j]:
                            return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Dict to count how many choices each value eliminates
        constraints = {}
        
        # Get unassigned neighbors of var
        unassigned_neighbors = [n for n in self.crossword.neighbors(var) 
                                if n not in assignment]
        
        for val in self.domains[var]:
            eliminated_count = 0
            
            for neighbor in unassigned_neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap:
                    i, j = overlap
                    
                    # Count values in neighbor's domain that would be eliminated
                    for neighbor_val in self.domains[neighbor]:
                        if val[i] != neighbor_val[j]:
                            eliminated_count += 1
            
            constraints[val] = eliminated_count
        
        # Return values sorted by how many constraints they impose (least first)
        return sorted(self.domains[var], key=lambda val: constraints[val])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [var for var in self.crossword.variables 
                    if var not in assignment]
        
        # Sort by: 1) Domain size (min), 2) Degree (max for ties)
        return min(
            unassigned,
            key=lambda var: (
                len(self.domains[var]), 
                -len(self.crossword.neighbors(var))
            )
        )

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment
        
        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        
        # Try to assign a value to the variable
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            
            # Check if assignment is consistent
            if self.consistent(assignment):
                # Recursive call
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            
            # If we reach here, the assignment failed, remove it and try again
            del assignment[var]
        
        # No solution found
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
