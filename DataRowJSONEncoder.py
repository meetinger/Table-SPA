from json import JSONEncoder

from DataRow import DataRow


class DataRowJSONEncoder(JSONEncoder):
    def default(self, o: DataRow) -> dict:
        return o.to_dict()