import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def scrape_website(url: str) -> str:
    """Scrapes content from a website and returns text content."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text(separator='\\n', strip=True)
        return text_content
    except requests.exceptions.Timeout:
        return f"Error: Request to '{url}' timed out."
    except requests.exceptions.RequestException as e:
        return f"Error scraping website '{url}': {e}"
    except Exception as e:
        return f"Error scraping website '{url}': {e}"

def google_search(query: str) -> str:
    """Performs a Google search and returns snippets from search results."""
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} # Mimic browser user-agent
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        search_results = []
        for result_block in soup.find_all('div', class_='tF2Cxc'): # Class name may vary, inspect Google search page
            link_element = result_block.find('a', href=True)
            title_element = result_block.find('h3')
            snippet_element = result_block.find('div',class_='VwiC3b')
            if link_element and title_element and snippet_element:
                link = link_element['href']
                title = title_element.text
                snippet = snippet_element.text
                search_results.append(f"Title: {title}\\nLink: {link}\\nSnippet: {snippet}\\n---")
        return "\\n".join(search_results) if search_results else "No relevant search results found."
    except requests.exceptions.Timeout:
        return "Error: Google search request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error performing Google search: {e}"
    except Exception as e:
        return f"Error performing Google search: {e}"

def get_most_voted_coding_forum_answers_to_similar_problems(query: str, forum_url: str) -> str:
    """
    Searches a coding forum (e.g., Stack Overflow) for answers to similar problems and returns the most voted answers.
    forum_url: Base URL of the coding forum (e.g., 'https://stackoverflow.com')
    """
    search_query = quote_plus(query)
    search_url = f"{forum_url}/search?q={search_query}" # Example for Stack Overflow

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} # Mimic browser user-agent

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        answers = []
        if "stackoverflow" in forum_url: # Example for stackoverflow.com
            question_summaries = soup.find_all('div', class_='s-post-summary')
            for question_summary in question_summaries:
                question_link_element = question_summary.select_one('.s-link')
                question_link = forum_url + question_link_element['href'] if question_link_element else "Link not found"
                question_title = question_link_element.text if question_link_element else "Title not found"
                answer_count_element = question_summary.select_one('.s-post-summary--stats-item__emphasized')
                answer_count = answer_count_element.text.strip() if answer_count_element else "No answers"
                vote_count_element = question_summary.select_one('.js-vote-count')
                vote_count = vote_count_element.text.strip() if vote_count_element else "0"

                answers.append({
                    "question_title": question_title,
                    "question_link": question_link,
                    "answer_count": answer_count,
                    "vote_count": vote_count
                })
        else:
            return "Error: Forum URL not supported for answer retrieval. Only stackoverflow.com is supported in this tool."

        sorted_answers = sorted(answers, key=lambda x: int(x["vote_count"]), reverse=True)[:5] # Get top 5 voted answers
        search_results = []
        for answer in sorted_answers:
            search_results.append(f"Question: {answer['question_title']}\\nLink: {answer['question_link']}\\nAnswers: {answer['answer_count']}\\Votes: {answer['vote_count']}\\n---")
        return "\\n".join(search_results) if search_results else "No relevant answers found in coding forum."

    except requests.exceptions.Timeout:
        return f"Error: Coding forum search request timed out for '{forum_url}'."
    except requests.exceptions.RequestException as e:
        return f"Error performing coding forum search for '{forum_url}': {e}"
    except Exception as e:
        return f"Error performing coding forum search for '{forum_url}': {e}"