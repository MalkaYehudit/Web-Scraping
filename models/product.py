class Product:
    def __init__(self, name, price, store):
        self.name = name
        self.price = float(price)  # שים לב לוודא שזו מספר
        self.store = store

    def __repr__(self):
        return f"{self.store}: {self.name} - {self.price} ש\"ח"
