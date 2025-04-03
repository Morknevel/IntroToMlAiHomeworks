import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },
    "trait": {
        # Probability of trait given gene
        2: {
            True: 0.65,
            False: 0.35
        },
        1: {
            True: 0.56,
            False: 0.44
        },
        0: {
            True: 0.01,
            False: 0.99
        }
    },
    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")

    # Load data from file
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all possible combinations of gene counts
        for gene_counts in all_gene_combinations(names):
            # Check if gene count configuration violates known information
            fails_evidence = any(
                (people[person]["gene"] is not None and
                 people[person]["gene"] != gene_counts[person])
                for person in names
            )
            if fails_evidence:
                continue

            # Calculate probability under this configuration
            p = joint_probability(people, gene_counts, have_trait)

            # Update probabilities with new joint probability
            update(probabilities, gene_counts, have_trait, p)

    # Normalize probabilities
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must be blank for unknown parents.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None),
                "gene": int(row["gene"]) if row.get("gene") else None
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def all_gene_combinations(people):
    """
    Return a list of all possible gene count combinations.
    Each combination is a dictionary mapping a person to a gene count (0, 1, or 2).
    """
    # Get list of people
    people_list = list(people)

    # All possible gene combinations (0, 1, or 2 copies for each person)
    gene_options = [0, 1, 2]

    # Generate all combinations
    all_combinations = itertools.product(gene_options, repeat=len(people_list))

    # Convert to dictionary format
    result = []
    for combo in all_combinations:
        gene_counts = dict(zip(people_list, combo))
        result.append(gene_counts)

    return result


def joint_probability(people, gene_counts, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `have_trait` has the trait, and
        * everyone not in set `have_trait` does not have the trait, and
        * everyone in `gene_counts` has the specified number of genes.
    """
    probability = 1.0

    # Calculate probability for each person
    for person in people:
        gene_count = gene_counts[person]
        trait = person in have_trait

        # Initialize person's probability
        person_prob = 1.0

        # For genes: first handle parents, then no parents
        mother = people[person]["mother"]
        father = people[person]["father"]

        # If person has no parents in the data
        if mother is None and father is None:
            # Use unconditional probability
            person_prob *= PROBS["gene"][gene_count]
        else:
            # Calculate based on parents
            # Probability of inheriting gene from mother
            mother_gene_count = gene_counts[mother]
            father_gene_count = gene_counts[father]

            # Probability of mother passing gene
            if mother_gene_count == 0:
                mother_passing = PROBS["mutation"]
            elif mother_gene_count == 1:
                mother_passing = 0.5
            else:  # mother_gene_count == 2
                mother_passing = 1 - PROBS["mutation"]

            # Probability of father passing gene
            if father_gene_count == 0:
                father_passing = PROBS["mutation"]
            elif father_gene_count == 1:
                father_passing = 0.5
            else:  # father_gene_count == 2
                father_passing = 1 - PROBS["mutation"]

            # Calculate probability based on gene count
            if gene_count == 0:
                # Neither parent passes gene
                person_prob *= (1 - mother_passing) * (1 - father_passing)
            elif gene_count == 1:
                # Either mother or father passes gene, but not both
                person_prob *= (mother_passing * (1 - father_passing) +
                                father_passing * (1 - mother_passing))
            else:  # gene_count == 2
                # Both parents pass gene
                person_prob *= mother_passing * father_passing

        # For trait: use conditional probability based on gene count
        person_prob *= PROBS["trait"][gene_count][trait]

        # Multiply by person's probability
        probability *= person_prob

    return probability


def update(probabilities, gene_counts, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    """
    for person in probabilities:
        gene_count = gene_counts[person]
        trait = person in have_trait

        # Update gene distribution
        probabilities[person]["gene"][gene_count] += p

        # Update trait distribution
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution is normalized.
    """
    for person in probabilities:
        # Normalize gene distribution
        gene_total = sum(probabilities[person]["gene"].values())
        for gene_count in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene_count] /= gene_total

        # Normalize trait distribution
        trait_total = sum(probabilities[person]["trait"].values())
        for trait_value in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait_value] /= trait_total


if __name__ == "__main__":
    main()