class DataRow:
    def __init__(self, row):
        self.id = row[0]
        self.date = row[1]
        self.name = row[2]
        self.amount = row[3]
        self.distance = row[4]

    def __str__(self):
        return f'DataRow{{id: {self.id}, date: {self.date}, name: {self.name}, ' \
               f'amount: {self.amount}, distance: {self.distance}}} '

    def to_dict(self):
        tmp = {
            'id': self.id,
            'date': str(self.date),
            'name': self.name,
            'amount': self.amount,
            'distance': self.distance
        }

        return tmp
