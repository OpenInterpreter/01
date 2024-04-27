import requests
import json

class Browser:
    def __init__(self, computer):
        self.computer = computer

    def search(self, query):
     
        try:
           
            response = requests.get(
                f'{self.computer.api_base.strip("/")}/browser/search',
                params={"query": query},
            )
            response.raise_for_status()  
            return response.json()["result"]
        except Exception as e:
            print(f"Error with OpenInterpreter API: {e}. Trying with Google search.")
            return self.fallback_search(query)

    def fallback_search(self, query):
        """
        Fallback search using Google search when the primary API fails.
        """
        try:
            from googlesearch import search
    
            for result in search(query, num=1, stop=1, pause=2):
                return json.dumps({'result': result})
        except Exception as e:
            print(f"Error in Google search: {e}")
            return json.dumps({'error': 'Both primary and fallback searches failed'})

# Example usage
if __name__ == "__main__":
    computer = Computer(api_base='https://api.openinterpreter.com/v0/')
    browser = Browser(computer)
    print(browser.search("What is the weather going to be like tomorrow in Charlotte, NC?"))