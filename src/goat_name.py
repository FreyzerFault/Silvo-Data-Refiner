import random

class Fabrica_de_Cabras:
  
  def __init__(self):
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
    random.shuffle(self.nombres)
    self.count = 0

fabrica = Fabrica_de_Cabras()

def get_goat_name(index = -1) -> str:
  nombre = fabrica.nombres[fabrica.count] if index == -1  else fabrica.nombres[index]
  fabrica.count += 1
  fabrica.count = fabrica.count % len(fabrica.nombres)
  return nombre