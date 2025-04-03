import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initialize the probability distribution dictionary
    distribution = {}
    num_pages = len(corpus)
    
    # Get the links from the current page
    links = corpus[page]
    
    # If the page has no links, we treat it as if it has links to all pages
    if not links:
        # Equal probability for all pages
        for p in corpus:
            distribution[p] = 1 / num_pages
    else:
        # Calculate probability for random selection (1 - damping_factor)
        random_prob = (1 - damping_factor) / num_pages
        
        # Calculate probability for following a link (damping_factor / number of links)
        link_prob = damping_factor / len(links)
        
        # Set initial probabilities based on random selection
        for p in corpus:
            distribution[p] = random_prob
        
        # Add link probabilities
        for link in links:
            distribution[link] += link_prob
    
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize the PageRank dictionary with zeros
    pagerank = {page: 0 for page in corpus}
    
    # Choose a random page to start
    current_page = random.choice(list(corpus.keys()))
    
    # Update the first sample
    pagerank[current_page] += 1
    
    # Perform the remaining n-1 samples
    for _ in range(n - 1):
        # Get the probability distribution for the next page
        distribution = transition_model(corpus, current_page, damping_factor)
        
        # Choose the next page based on the distribution
        pages = list(distribution.keys())
        weights = list(distribution.values())
        current_page = random.choices(pages, weights=weights, k=1)[0]
        
        # Update the count for the selected page
        pagerank[current_page] += 1
    
    # Normalize counts to get probabilities
    for page in pagerank:
        pagerank[page] /= n
    
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Number of pages in the corpus
    num_pages = len(corpus)
    
    # Initialize PageRank with equal values for all pages
    pagerank = {page: 1 / num_pages for page in corpus}
    
    links_to = {page: [] for page in corpus}
    for page, links in corpus.items():
        if not links:
            for p in corpus:
                if p != page:  # Exclude self-links as per project specs
                    links_to[p].append(page)
        else:
            for link in links:
                links_to[link].append(page)
    

    while True:
        new_pagerank = {}
        max_change = 0
        
        for page in corpus:
            # Start with the random surfer probability
            new_rank = (1 - damping_factor) / num_pages
            
            for linking_page in links_to[page]:
                num_links = len(corpus[linking_page]) if corpus[linking_page] else num_pages
                
                new_rank += damping_factor * (pagerank[linking_page] / num_links)
            
            change = abs(new_rank - pagerank[page])
            max_change = max(max_change, change)
            
            new_pagerank[page] = new_rank
        
        pagerank = new_pagerank

        if max_change < 0.001:
            break
    
    total = sum(pagerank.values())
    for page in pagerank:
        pagerank[page] /= total
    
    return pagerank


if __name__ == "__main__":
    main()