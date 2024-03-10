from kindwise import PlantApi

class PlantClient:
    def __init__(self, api_key):
        self.api = PlantApi(api_key)

    def identify(self, file_path: str):
        identification = self.api.identify(file_path, details=['url', 'common_names'])

        return identification.result.classification.suggestions[0]