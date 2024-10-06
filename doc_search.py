import csv
import os
from datetime import datetime
from difflib import SequenceMatcher

class ProSearch:
    def __init__(self, db_file="search_db.csv"):
        self.db_file = db_file
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'title', 'content', 'tags', 'date_added'])
    
    def add_document(self, title, content, tags):
        with open(self.db_file, 'a', newline='') as file:
            writer = csv.writer(file)
            doc_id = self.get_next_id()
            writer.writerow([doc_id, title, content, ','.join(tags), datetime.now()])
        print(f"Document '{title}' added successfully!")
    
    def search(self, query, threshold=0.6):
        results = []
        with open(self.db_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Search in title, content, and tags
                title_similarity = SequenceMatcher(None, query.lower(), row['title'].lower()).ratio()
                content_similarity = SequenceMatcher(None, query.lower(), row['content'].lower()).ratio()
                tag_similarity = max([SequenceMatcher(None, query.lower(), tag.lower()).ratio() 
                                   for tag in row['tags'].split(',')], default=0)
                
                max_similarity = max(title_similarity, content_similarity, tag_similarity)
                if max_similarity >= threshold:
                    results.append({
                        'id': row['id'],
                        'title': row['title'],
                        'preview': row['content'][:100] + '...',
                        'relevance': max_similarity
                    })
        
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
    
    def get_next_id(self):
        try:
            with open(self.db_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                return str(sum(1 for row in reader) + 1)
        except:
            return "1"

def main():
    search_engine = ProSearch()
    
    while True:
        print("\n=== Pro Search Engine ===")
        print("1. Add new document")
        print("2. Search documents")
        print("3. Exit")
        
        choice = input("Choose an option (1-3): ")
        
        if choice == "1":
            title = input("Enter document title: ")
            content = input("Enter document content: ")
            tags = input("Enter tags (comma-separated): ").split(',')
            search_engine.add_document(title, content, tags)
            
        elif choice == "2":
            query = input("Enter search query: ")
            results = search_engine.search(query)
            
            if results:
                print("\nSearch Results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['title']} (Relevance: {result['relevance']:.2f})")
                    print(f"Preview: {result['preview']}")
            else:
                print("\nNo results found.")
                
        elif choice == "3":
            print("Thank you for using Pro Search!")
            break

if __name__ == "__main__":
    main()