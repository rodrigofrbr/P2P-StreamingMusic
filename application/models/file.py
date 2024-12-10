class File:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    @staticmethod
    def to_json(data):
        return {
            'name': data.name,
            'path': data.path
        }
    
    @staticmethod
    def from_json(data):
        return File(data['name'], data['path'])