import csv
import sys
import collections

names = {}

people = {}

movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    Expects three files: people.csv, movies.csv, and stars.csv in the given directory.
    """
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            lower_name = row["name"].lower()
            if lower_name in names:
                names[lower_name].add(row["id"])
            else:
                names[lower_name] = {row["id"]}
    
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }
    
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                continue

def person_id_for_name(name):
    """
    Returns the person_id for a person's name.
    If multiple persons have the same name, prompts the user to select the intended person.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            print(f"ID: {person_id}, Name: {person['name']}, Birth: {person['birth']}")
        try:
            chosen_id = input("Intended Person ID: ")
            if chosen_id in person_ids:
                return chosen_id
        except ValueError:
            return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for all people that are connected
    to the given person via a shared movie.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person in movies[movie_id]["stars"]:
            if person != person_id:
                neighbors.add((movie_id, person))
    return neighbors

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs that connect the source
    to the target using breadth-first search. If no possible path, returns None.
    """
  
    frontier = collections.deque()
    frontier.append((None, source, []))
    explored = set()
    
    while frontier:
        current_movie, current_person, path = frontier.popleft()
        if current_person == target:
            return path
        explored.add(current_person)
        
        for movie, person in neighbors_for_person(current_person):
            if person not in explored and not any(node[1] == person for node in frontier):
                new_path = path + [(movie, person)]
                if person == target:
                    return new_path
                frontier.append((movie, person, new_path))
    
    return None

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python degrees.py [directory]")
    
    directory = sys.argv[1]
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")
    
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")
    
    path = shortest_path(source, target)
    
    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i+1][1]]["name"]
            movie = movies[path[i+1][0]]["title"]
            print(f"{i+1}: {person1} and {person2} starred in {movie}")

if __name__ == "__main__":
    main()