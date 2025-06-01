from search_engine import SearchEngine

if __name__ == "__main__":
    engine = SearchEngine("data")
    query = input("Enter your search query: ")
    results = engine.search(query)
    print("Results:")
    for file, score in results:
        print(f"{file} (score: {score:.4f})")
