import contextlib
import io
from urllib.parse import quote_plus

from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

from sandbox_toolkit.logs.logging import logger
from src.sandbox_toolkit.infra.sandbox_base.schema_models.internal_schemas import (
    ToolReturn,
)


def scrape_website(url: str) -> ToolReturn:
    """Scrapes content from a website and returns text content."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting scrape_website with url: {url}")
            try:
                class WebsiteSpider(Spider):
                    name = "website_spider"
                    start_urls = [url]

                    def parse(self, response):
                        text_content = response.text
                        self.crawler.stats.set_value('text_content', text_content)

                process = CrawlerProcess({
                    'LOG_LEVEL': 'ERROR',
                    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
                })
                process.crawl(WebsiteSpider)
                process.start()
                text_content = process.crawler.stats.get_value('text_content')
                process.stop()
                if text_content:
                    logger.info(f"Finished scrape_website with url: {url}, output: {text_content[:100]}...")
                    return ToolReturn(return_value=text_content, std_out="", std_err="", logs="")
                else:
                    logger.warning(f"No content found for url: {url}")
                    return ToolReturn(return_value="No content found.", std_out="", std_err="", logs="")
            except Exception as e:
                logger.error(f"Error scraping website: {e}")
                return ToolReturn(return_value=f"Error scraping website: {e}", std_out="", std_err="", logs="")
            finally:
                logger.info(f"Finished scrape_website with url: {url}")

def google_search(query: str) -> ToolReturn:
    """Performs a Google search and returns snippets from search results."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting google_search with query: {query}")
            try:
                search_url = f"https://www.google.com/search?q={quote_plus(query)}"
                class GoogleSpider(Spider):
                    name = "google_spider"
                    start_urls = [search_url]

                    def parse(self, response):
                        search_results = []
                        for result_block in response.css('div.tF2Cxc'):
                            link_element = result_block.css('a::attr(href)').get()
                            title_element = result_block.css('h3::text').get()
                            snippet_element = result_block.css('div.VwiC3b::text').get()
                            if link_element and title_element and snippet_element:
                                search_results.append(f"Title: {title_element}\\nLink: {link_element}\\nSnippet: {snippet_element}\\n---")
                        self.crawler.stats.set_value('search_results', "\\n".join(search_results) if search_results else "No relevant search results found.")

                process = CrawlerProcess({
                    'LOG_LEVEL': 'ERROR',
                    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
                })
                process.crawl(GoogleSpider)
                process.start()
                search_results = process.crawler.stats.get_value('search_results')
                process.stop()
                if search_results:
                    logger.info(f"Finished google_search with query: {query}, output: {search_results[:100]}...")
                    return ToolReturn(return_value=search_results, std_out="", std_err="", logs="")
                else:
                    logger.warning(f"No search results found for query: {query}")
                    return ToolReturn(return_value="No relevant search results found.", std_out="", std_err="", logs="")
            except Exception as e:
                logger.error(f"Error performing Google search: {e}")
                return ToolReturn(return_value=f"Error performing Google search: {e}", std_out="", std_err="", logs="")
            finally:
                logger.info(f"Finished google_search with query: {query}")

def get_most_voted_coding_forum_answers_to_similar_problems(query: str, forum_url: str) -> ToolReturn:
    """
    Searches a coding forum (e.g., Stack Overflow) for answers to similar problems and returns the most voted answers.
    forum_url: Base URL of the coding forum (e.g., 'https://stackoverflow.com')
    """
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting get_most_voted_coding_forum_answers_to_similar_problems with query: {query} and forum_url: {forum_url}")
            try:
                search_query = quote_plus(query)
                search_url = f"{forum_url}/search?q={search_query}"
                class ForumSpider(Spider):
                    name = "forum_spider"
                    start_urls = [search_url]

                    def parse(self, response):
                        answers = []
                        if "stackoverflow" in forum_url:
                            question_summaries = response.css('div.s-post-summary')
                            for question_summary in question_summaries:
                                question_link_element = question_summary.css('.s-link::attr(href)').get()
                                question_link = forum_url + question_link_element if question_link_element else "Link not found"
                                question_title = question_summary.css('.s-link::text').get() if question_link_element else "Title not found"
                                answer_count_element = question_summary.css('.s-post-summary--stats-item__emphasized::text').get()
                                answer_count = answer_count_element.strip() if answer_count_element else "No answers"
                                vote_count_element = question_summary.css('.js-vote-count::text').get()
                                vote_count = vote_count_element.strip() if vote_count_element else "0"

                                answers.append({
                                    "question_title": question_title,
                                    "question_link": question_link,
                                    "answer_count": answer_count,
                                    "vote_count": vote_count
                                })
                        else:
                            self.crawler.stats.set_value('search_results', "Error: Forum URL not supported for answer retrieval. Only stackoverflow.com is supported in this tool.")
                            return

                        sorted_answers = sorted(answers, key=lambda x: int(x["vote_count"]), reverse=True)[:5]
                        search_results = []
                        for answer in sorted_answers:
                            search_results.append(f"Question: {answer['question_title']}\\nLink: {answer['question_link']}\\nAnswers: {answer['answer_count']}\\Votes: {answer['vote_count']}\\n---")
                        self.crawler.stats.set_value('search_results', "\\n".join(search_results) if search_results else "No relevant answers found in coding forum.")

                process = CrawlerProcess({
                    'LOG_LEVEL': 'ERROR',
                    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
                })
                process.crawl(ForumSpider)
                process.start()
                search_results = process.crawler.stats.get_value('search_results')
                process.stop()
                if search_results:
                    logger.info(f"Finished get_most_voted_coding_forum_answers_to_similar_problems with query: {query} and forum_url: {forum_url}, output: {search_results[:100]}...")
                    return ToolReturn(return_value=search_results, std_out="", std_err="", logs="")
                else:
                    logger.warning(f"No search results found for query: {query} in forum: {forum_url}")
                    return ToolReturn(return_value="No relevant answers found in coding forum.", std_out="", std_err="", logs="")
            except Exception as e:
                logger.error(f"Error performing coding forum search: {e}")
                return ToolReturn(return_value=f"Error performing coding forum search for '{forum_url}': {e}", std_out="", std_err="", logs="")
            finally:
                logger.info(f"Finished get_most_voted_coding_forum_answers_to_similar_problems with query: {query} and forum_url: {forum_url}")
