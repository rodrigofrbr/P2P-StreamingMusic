from models.file import File


class Client:
    def __init__(self, name: str, address: str, files: list[File], is_connected : bool):
        self.name = name
        self.address = address
        self.files = files
        self.is_connected = is_connected

    def add_file(self, file : File):
        self.files.append(file)
    
    @staticmethod
    def to_json(data):
        return {
            'name': data.name,
            'address': data.address,
            'files': [File.to_json(file) for file in data.files],
            'is_connected': data.is_connected
        }
    
    @staticmethod
    def from_json(data):
        files = [File.from_json(file_data) for file_data in data['files']]
        return Client(data['name'], data['address'], files, data['is_connected'])
