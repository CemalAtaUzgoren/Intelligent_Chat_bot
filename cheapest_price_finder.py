import json
import os
import sys

class PriceFinder(object):
    def __init__(self):
        self.expected_files = ["greateranglia.json", "LNER.json", "nationalrail.json", "trainpal.json", 
                               "southernRailways.json" , "mytrainticket.json"]

    def compare_prices(self):
        final_dict = {}
        for file in self.expected_files:
            # Check which sites fetched the data. Ignore the ones could not fetch
            get_file_size = os.path.getsize(file)
            if get_file_size == 0:
                continue
            else:
                with open(file) as f:
                    data = json.load(f)
                    final_dict[file] = [data['price'], data['url']]
        # Sort dict in ascending order to find cheapest key value first
        sorted_dict = dict(sorted(final_dict.items(), key=lambda item: item[1][0]))
        # print(sorted_dict)
        # Returns tuple where 1st tuple is site name and 2nd is the price value
        return  next(iter(sorted_dict)), next(iter(sorted_dict.values()))


if __name__ == "__main__":
    obj = PriceFinder()
    obj.compare_prices()