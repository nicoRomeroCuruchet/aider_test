import concurrent.futures
import requests

class NetworkRequestHandler:
    """
    A class to handle concurrent network requests using ThreadPoolExecutor.
    
    Attributes:
        max_workers (int): The maximum number of threads that can be used for executing calls concurrently.
    """

    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def fetch(self, url):
        """
        Fetches the content of a given URL using a GET request.
        
        Args:
            url (str): The URL to fetch.
            
        Returns:
            str: The content of the response if successful, None otherwise.
        """
        try:
            with self.executor.submit(requests.get, url) as future:
                response = future.result()
                response.raise_for_status()  # Raises an HTTPError for bad responses
                return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def shutdown(self):
        """
        Shuts down the ThreadPoolExecutor.
        """
        self.executor.shutdown(wait=True)

if __name__ == '__main__':
    handler = NetworkRequestHandler(max_workers=10)
    
    urls = [
        'https://www.example.com',
        'https://www.python.org',
        'https://www.github.com'
    ]
    
    results = [handler.fetch(url) for url in urls]
    
    for result in results:
        if result:
            print(result[:200])  # Print the first 200 characters of each response
    
    handler.shutdown()
