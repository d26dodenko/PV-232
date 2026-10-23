# fare.py

def count_fare(distance_km: float, age: int, is_preferential: bool, is_night: bool) -> int:
	"""
	Расчет стоимости проезда.

	Бизнес-правила:
	1. Если  distance_km <= 0 или age < 0 или age > 116 или is_preferential и is_night не булевые значения - ValueError
 	2. Если distance_km <= 2.49 - стоимость проезда = 25
 	3. Иначе
 	   - стоимость проезда = 25 + (distance_km - 2.49) * 2.5
 	4. Если is_night - fare = fare * 1.2
 	5. Если льготный проезд - проезд бесплатный
 	6. Если возраст < 5 - проезд бесплатный
	"""
	if distance_km <= 0:
		raise ValueError('distance must be > 0')
	if age < 0:
		raise ValueError('Age must be >= 0')
	if age > 116:
		raise ValueError('Age must be <= 116')
	if not isinstance(is_preferential, bool):
		raise ValueError('is_preferential  must be bool')
	if not isinstance(is_night, bool):
		raise ValueError('is_night must be bool')

	if age < 5 or is_preferential:
		return 0
	if distance_km <= 2.49:
		fare = 25
	else:
		fare = 25 + (distance_km - 2.49) * 2.5
	if is_night:
		fare = fare * 1.2
	return round(fare)

