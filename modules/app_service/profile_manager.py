import os
import json
class ProfileManager:
    @staticmethod
    def get_profiles():
        if not os.path.exists('profiles'):
            os.makedirs('profiles')
        return [f[:-5] for f in os.listdir('profiles') if f.endswith('.json')]

    @staticmethod
    def save_profile(name, data):
        with open(f'profiles/{name}.json', 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load_profile(name):
        with open(f'profiles/{name}.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def delete_profile(name):
        os.remove(f'profiles/{name}.json')
