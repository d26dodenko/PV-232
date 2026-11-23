def calc_discount(price, count):
  if price <= 0:
    raise ValueError("error: price must be positive")
  if count <= 0:
    raise ValueError("error: count must be positive")
  
  discount = 0.0
  
  if 1 <= count <= 10:
      discount += 0.01
  elif 11 <= count <= 20:
      discount += 0.02
  elif 21 <= count <= 30:
      discount += 0.04
  elif 31 <= count <= 50:
      discount += 0.06
  elif 51 <= count <= 70:
      discount += 0.08
  elif count > 70:
      discount += 0.09

  return round(price * (1 - discount))