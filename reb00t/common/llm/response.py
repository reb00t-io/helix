import json
import re

def extract_with_regex(xml_string, tag_name):
    # This regex pattern matches the content within the tag, handling nested tags as well
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    results = re.findall(pattern, xml_string, re.DOTALL)
    return [result.strip() for result in results] if results else []

class Response:
    def __init__(self, xml_string, tags=[], lazy=False):
        self.text = xml_string
        self.data = None if lazy else {tag: extract_with_regex(self.text, tag) for tag in tags}

    def get(self, tag_name):
        res = self.get_all(tag_name)
        return res[0] if res else None

    def get_all(self, tag_name):
        return self.data.get(tag_name) if self.data else extract_with_regex(self.text, tag_name)

    def tags(self):
        return self.data.keys() if self.data else []

class JsonResponse:
    def __init__(self, json_string):
        self.text = json_string
        self.data = json.loads(json_string)

    def get(self, tag_name):
        return self.data.get(tag_name)

    def tags(self):
        # return all keys in the JSON data
        return self.data.keys() if self.data else []
