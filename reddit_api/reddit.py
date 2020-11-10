import json
import requests

class Reddit:
    
    def __init__(self):
        pass

    def programming_articles(self):
        
        try:   
            articles = self.request()
            respon = self.get_reddit_articles(articles)
            return respon

        except :
            print("Invalid Subject")

    
    def request(self, subject):
            
        header = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
        }

        url = "https://www.reddit.com/r/{}/.json".format(subject)
        response = requests.get(url, headers=header)

        return response.json()

    def get_reddit_articles(self, subject):
        
        self.subject = subject
        articles = self.request(subject)
        keys = ["title", 'author_fullname', "ups", "downs", "subreddit", "created", "num_comments"]
         
        items = []

        try:
            for article in articles["data"]["children"]:

                item = {}

                for key in keys:
                    item[key] = article["data"][key]
                items.append(item)
            
            with open (subject + "_articles.json", "w") as json_file:
                json.dump(items, json_file, indent=4)

        except KeyError:
            print("Invalid subject")


if __name__ == "__main__":
    rd = Reddit()
    rd.get_reddit_articles("nba")