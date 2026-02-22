import concurrent.futures
import requests

class NetworkRequestHandler:
    """
    A class to handle concurrent network requests using ThreadPoolExecutor.
    
    Attributes:
        max_workers (int): The maximum number of threads that can be used for executing calls concurrently.
        session (requests.Session): A session object to reuse TCP connections.
    """

    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def fetch(self, url, timeout=10):
        """
        Fetches the content of a given URL using a GET request.
        
        Args:
            url (str): The URL to fetch.
            timeout (int): The timeout for the request in seconds.
            
        Returns:
            str: The content of the response if successful, None otherwise.
        """
        try:
            with self.executor.submit(self.session.get, url, timeout=timeout) as future:
                response = future.result()
                response.raise_for_status()  # Raises an HTTPError for bad responses
                return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def fetch_all(self, urls, timeout=10):
        """
        Fetches the content of multiple URLs concurrently.
        
        Args:
            urls (list): A list of URLs to fetch.
            timeout (int): The timeout for each request in seconds.
            
        Returns:
            list: A list of responses or None if a request failed.
        """
        with self.executor as executor:
            futures = {executor.submit(self.session.get, url, timeout=timeout): url for url in urls}
            results = []
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    response = future.result()
                    response.raise_for_status()  # Raises an HTTPError for bad responses
                    results.append(response.text)
                except requests.RequestException as e:
                    print(f"Failed to fetch {url}: {e}")
                    results.append(None)
            return results

    def shutdown(self):
        """
        Shuts down the ThreadPoolExecutor and closes the session.
        """
        self.executor.shutdown(wait=True)
        self.session.close()

if __name__ == '__main__':
    handler = NetworkRequestHandler(max_workers=10)
    
    urls = [
        'https://www.example.com',
        'https://www.python.org',
        'https://www.github.com'
    ]
    
    results = handler.fetch_all(urls, timeout=5)
    
    for result in results:
        if result:
            print(result[:200])  # Print the first 200 characters of each response
    
    handler.shutdown()
