import requests
from bs4 import BeautifulSoup

class HackerNewsClient:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com"

    def fetch_hackernews_top_stories(self):
        response = requests.get(self.base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        stories = soup.find_all("tr", class_="athing")

        top_stories = []
        for story in stories:
            title_tag = story.find("span", class_="titleline")
            if title_tag:
                title=title_tag.find("a").text
                link=title_tag.find("a")['href']
                top_stories.append({
                    "title": title,
                    "link": link
                })

        return top_stories

if __name__ == "__main__":
    hacker_news_client = HackerNewsClient()
    top_stories = hacker_news_client.fetch_hackernews_top_stories()
    for idx,story in enumerate(top_stories,start=1):
        print(f"{idx}. {story['title']} - {story['link']}")