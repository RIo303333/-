#def uppercase_result(old_func):
#
#    def new_func(*args ,**kwargs):
#        res = old_func(*args,**kwargs)
#        if isinstance(res , str):
#            return res.upper()
#        return res
#    return new_func
#@uppercase_result
#def get_message():
#    return "Привет, мир!"
#print(get_message())

#def log_function_call(old_func):
#
#    def new_func(*args ,**kwargs):
#        print(old_func.__name__,args)
#        return old_func(*args)
#    return new_func
#@log_function_call
#def add(a, b):
#    return a + b
#print(add(5, 3))
#def check_division(old_func):
#    def new_func(a,b):
#       if a != 0 and b != 0:
#           return a / b
#       else:
#           return f' Деление невозможно'
#       return old_func(*args)
#    return new_func
#@check_division
#def divide(a, b):
#    return a / b
#print(divide(10, 2))
#def save_result(old_func):
#    def new_func(*args, **kwargs):
#        res = old_func(*args,**kwargs)
#        with open('result.txt', 'a', encoding='utf-8') as f:
#            print(res, file=f)
#        return res
#    return new_func

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class Seat:
    """Класс отдельного места в самолете."""
    def __init__(self, seat_id: str, seat_class: str):
        self.seat_id = seat_id  # Например, '1A', '12B'
        self.seat_class = seat_class  # 'Economy', 'Business', 'First'
        self.is_booked = False

    def __repr__(self):
        status = "X" if self.is_booked else "O"
        return f"{self.seat_id}({status})"


class Flight:
    """Класс рейса."""
    def __init__(self, flight_number: str, origin: str, destination: str, 
                 departure_time: datetime, duration: timedelta,
                 has_meals: bool = True, extra_baggage_allowed: bool = True):
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.duration = duration
        self.has_meals = has_meals
        self.extra_baggage_allowed = extra_baggage_allowed
        
        # Конфигурация салона: layout[row_index] = [Seat1, Seat2, ...]
        self.seats: Dict[str, Seat] = {}  # seat_id -> Seat
        self.layout: List[List[Seat]] = []
        self.class_seats: Dict[str, List[Seat]] = {}  # class_name -> list of Seats

    def configure_seats(self, layout_config: List[Tuple[str, int, int]]):
        """
        Настройка конфигурации салона.
        layout_config: список кортежей (класс, количество_рядов, мест_в_ряду)
        Пример: [('Business', 2, 4), ('Economy', 5, 6)]
        """
        self.seats.clear()
        self.layout.clear()
        self.class_seats.clear()

        row_counter = 1
        letters = "ABCDEFGHJK"

        for seat_class, num_rows, seats_per_row in layout_config:
            if seat_class not in self.class_seats:
                self.class_seats[seat_class] = []

            for _ in range(num_rows):
                row_seats = []
                for s_idx in range(seats_per_row):
                    seat_id = f"{row_counter}{letters[s_idx]}"
                    seat = Seat(seat_id, seat_class)
                    self.seats[seat_id] = seat
                    self.class_seats[seat_class].append(seat)
                    row_seats.append(seat)
                self.layout.append(row_seats)
                row_counter += 1

    def get_available_seats_count(self, seat_class: Optional[str] = None) -> int:
        """Возвращает количество свободных мест в классе (или всего на рейсе)."""
        if seat_class:
            seats = self.class_seats.get(seat_class, [])
            return sum(1 for s in seats if not s.is_booked)
        return sum(1 for s in self.seats.values() if not s.is_booked)

    def book_seats(self, seat_ids: List[str]) -> bool:
        """Бронирует указанные места."""
        for s_id in seat_ids:
            if s_id not in self.seats or self.seats[s_id].is_booked:
                return False  # Одно из мест не существует или уже занято

        for s_id in seat_ids:
            self.seats[s_id].is_booked = True
        return True

    def find_adjacent_seats(self, seat_class: str, count: int) -> List[List[str]]:
        """Ищет варианты нескольких свободных мест подряд в одном ряду."""
        adjacent_options = []
        for row in self.layout:
            current_group = []
            for seat in row:
                if seat.seat_class == seat_class and not seat.is_booked:
                    current_group.append(seat.seat_id)
                    if len(current_group) == count:
                        adjacent_options.append(list(current_group))
                        current_group.pop(0)  # Сдвигаем окно для нахождения всех перекрывающихся групп
                else:
                    current_group = []
        return adjacent_options

    def print_seating_chart(self):
        """Печатает план салона с указанием занятых (X) и свободных (O) мест."""
        print(f"\n--- План салона для рейса {self.flight_number} ({self.origin} -> {self.destination}) ---")
        print("Условные обозначения: [Место:O] — свободно, [Место:X] — занято\n")
        
        current_class = None
        for row in self.layout:
            row_class = row[0].seat_class if row else ""
            if row_class != current_class:
                current_class = row_class
                print(f"=== Класс: {current_class} ===")

            row_str = " ".join([f"[{s.seat_id}:{'X' if s.is_booked else 'O'}]" for s in row])
            print(row_str)
        print("-" * 50)


class FlightSystem:
    """Главная система управления аэропортами и рейсами."""
    def __init__(self):
        self.airports: set = set()
        self.flights: List[Flight] = []

    def add_airport(self, code: str):
        """Добавить аэропорт по IATA/ИКАО коду."""
        self.airports.add(code.upper())

    def add_flight(self, flight: Flight):
        """Добавить рейс в систему."""
        if flight.origin not in self.airports or flight.destination not in self.airports:
            raise ValueError("Аэропорт вылета или прибытия отсутствует в системе!")
        self.flights.append(flight)

    def search_nearest_flights(self, origin: str, destination: str, 
                               target_time: datetime, seat_class: Optional[str] = None, 
                               seats_count: int = 1,
                               time_preference: Optional[str] = None, # 'morning', 'afternoon', 'evening', 'night'
                               require_adjacent: bool = False,
                               has_meals: Optional[bool] = None,
                               extra_baggage: Optional[bool] = None) -> List[Flight]:
        """Универсальный поиск ближайших подходящих рейсов по критериям."""
        suitable_flights = []

        for flight in self.flights:
            if flight.origin != origin or flight.destination != destination:
                continue

            # Проверка наличия свободных мест
            if flight.get_available_seats_count(seat_class) < seats_count:
                continue

            # Проверка места рядом при необходимости
            if require_adjacent and seat_class:
                if not flight.find_adjacent_seats(seat_class, seats_count):
                    continue

            # Проверка специальных условий
            if has_meals is not None and flight.has_meals != has_meals:
                continue
            if extra_baggage is not None and flight.extra_baggage_allowed != extra_baggage:
                continue

            # Проверка временных предпочтений по времени суток
            if time_preference:
                hour = flight.departure_time.hour
                if time_preference == 'morning' and not (6 <= hour < 12):
                    continue
                elif time_preference == 'afternoon' and not (12 <= hour < 18):
                    continue
                elif time_preference == 'evening' and not (18 <= hour < 24):
                    continue
                elif time_preference == 'night' and not (0 <= hour < 6):
                    continue

            suitable_flights.append(flight)

        # Сортируем по близости к желаемому времени target_time
        suitable_flights.sort(key=lambda f: abs((f.departure_time - target_time).total_seconds()))
        return suitable_flights


# ==========================================
# Пример использования и проверки программы
# ==========================================
if __name__ == "__main__":
    system = FlightSystem()

    # 1. Добавление аэропортов
    system.add_airport("SVO")  # Москва (Шереметьево)
    system.add_airport("LED")  # Санкт-Петербург (Пулково)
    system.add_airport("AER")  # Сочи

    # 2. Создание и добавление рейсов
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    # Рейс 1: Утренний рейс SVO -> LED
    f1 = Flight("SU100", "SVO", "LED", 
                departure_time=now + timedelta(hours=3),  # Утро
                duration=timedelta(hours=1, minutes=30),
                has_meals=True, extra_baggage_allowed=True)
    # 1 ряд Business (2 места), 3 ряда Economy (4 места в ряду)
    f1.configure_seats([("Business", 1, 2), ("Economy", 3, 4)])

    # Рейс 2: Дневной рейс SVO -> LED
    f2 = Flight("SU102", "SVO", "LED", 
                departure_time=now + timedelta(hours=8),  # День
                duration=timedelta(hours=1, minutes=30),
                has_meals=False, extra_baggage_allowed=True)
    f2.configure_seats([("Business", 1, 2), ("Economy", 2, 4)])

    system.add_flight(f1)
    system.add_flight(f2)

    # 3. Бронирование некоторых мест на рейсе f1
    f1.book_seats(["1A", "2A", "2B"])

    # 4. Печать плана салона
    f1.print_seating_chart()

    # 5. Поиск ближайших рейсов
    print("--- Поиск ближайшего рейса SVO -> LED ---")
    results = system.search_nearest_flights("SVO", "LED", target_time=now, seat_class="Economy", seats_count=1)
    for flight in results:
        print(f"Найден рейс: {flight.flight_number}, Время вылета: {flight.departure_time.strftime('%H:%M')}")

    # 6. Поиск рейсов с несколькими свободными местами РЯДОМ
    print("\n--- Поиск рейсов с 2 мест рядом в Эконом-классе ---")
    adjacent_results = system.search_nearest_flights("SVO", "LED", target_time=now, 
                                                    seat_class="Economy", seats_count=2, 
                                                    require_adjacent=True)
    for flight in adjacent_results:
        options = flight.find_adjacent_seats("Economy", 2)
        print(f"Рейс {flight.flight_number}: доступные комбинации мест рядом -> {options}")

    # 7. Поиск утреннего рейса с наличием питания
    print("\n--- Поиск ближайшего УТРЕННЕГО рейса с включенным ПИТАНИЕМ ---")
    morning_meals = system.search_nearest_flights("SVO", "LED", target_time=now, 
                                                  time_preference="morning", has_meals=True)
    for flight in morning_meals:
        print(f"Рейс {flight.flight_number}, Вылет: {flight.departure_time.strftime('%H:%M')}, Питание: {flight.has_meals}")
