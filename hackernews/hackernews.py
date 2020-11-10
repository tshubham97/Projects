import json
import requests
import datetime


class HackerNews:
    
    def __init__(self):
        pass

    def get_top_stories(self):
        
        link = "https://hacker-news.firebaseio.com/v0/item"
        keys = ["title", "score", "by", "time", "descendants", "url"]
        top_url="https://hacker-news.firebaseio.com/v0/topstories.json"

        topstories = self._requests(top_url)

        if len(topstories) >= 30:
            top_30_stories  = topstories[0:30]

        else:
            print("Story list is less than 30")
            return
            
        items = []

        for story_id in top_30_stories:

            story_link = ("{link}/{id}.json").format(link=link, id=story_id)
            story = self._requests(story_link)
                                           
            item = {}

            time_new = story.get('time')
            time_new = datetime.datetime.utcfromtimestamp(story['time']).strftime("%H hours ago")

            for key in keys:
                if key == "by":
                    item["author"] = story.get(key)
                elif key == "score":
                    item["points"] = story.get(key)
                elif key == "descendants":
                    item["comments"] = story.get(key)
                elif key == "time":
                    item[key] = time_new
                elif key == "url":
                    item[key] = story.get(key)
                else:
                    item[key] = story.get(key)


            items.append(item)

        with open("news.json", "w") as news:
            json.dump(items, news, indent=4)

    def _requests(self,url):
        
        try:
            url_response = requests.get(url)
            if url_response.status_code == 404:
                print("URL not found")
            elif url_response.status_code == 200:
                pass
            response = json.loads(url_response.text)
            return response

        except json.JSONDecodeError:
            print("Invalid JSON")

        raise Exception ("No Json data found")


if __name__ == "__main__":
    hn = HackerNews()
    hn.get_top_stories()