import random

class Goat_Factory:
  
  def __init__(self, random = False):
    self.nombres = [
      "Asunción",
      "Concepción",
      "Dolores",
      "Rosita",
      "Lucía",
      "Lourdes",
      "Isabel",
      "Carmen",
      "Antonia",
      "Juani",
      "Fátima",
      "Roberta",
      "Loli",
      "Conchita",
      "Mercedes",
      "Encarni",
      "Susana", 
      "Carlota",
      "Lorena",
      "Amparo",
      "Eugenia",
      "Josefina",
      "Belén"
    ]
    if random:
      random.shuffle(self.nombres)
    else:
      self.nombres.sort()
    self.count = 0

fabrica = Goat_Factory()

def get_goat_name(index = -1) -> str:
  nombre = fabrica.nombres[fabrica.count] if index == -1  else fabrica.nombres[index]
  fabrica.count = (fabrica.count + 1) % len(fabrica.nombres)
  return nombre


if __name__ == '__main__':
  goats = []
  
  # Limitado a 100 veces por si acaso
  for i in range(0, 100):
    if input("Press Enter to get a goat name or write 'n' to exit") == 'n':
      exit()
    goats.append(get_goat_name())
    print(f"Goat Names:{goats}")