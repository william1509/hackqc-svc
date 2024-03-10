from kindwise import PlantApi

class PlantClient:
    def __init__(self, api_key):
        self.api = PlantApi(api_key)
    
    def identify(self, file_path: str):
        identification = self.api.identify(file_path, details=['url', 'common_names'])

        print('is plant' if identification.result.is_plant.binary else 'is not plant')
        return identification.result.classification.suggestions[0]
        
        for suggestion in identification.result.classification.suggestions:
            print(suggestion.name)
            print(f'probability {suggestion.probability:.2%}')
            print(suggestion.details['url'], suggestion.details['common_names'])
            print()