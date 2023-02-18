from random import randint


class ExceptionForTheEntireCode(Exception):
	pass


class ShotBehindTheBoard(ExceptionForTheEntireCode):
	def __str__(self):
		return '!! Ход за предел доски !!'


class InTheSamePlace(ExceptionForTheEntireCode):
	def __str__(self):
		return '!! Ход в эту клетку уже был !!'


class InternalExceptions(ExceptionForTheEntireCode):
	pass


class Dot:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def __repr__(self):
		return f'Dot({self.x},{self.y})'


class Board:
	def __init__(self, hid=False, size=9):
		self.size = size
		self.field = [['0'] * size for _ in range(size)]
		self.hid = hid
		self.ships = []
		self.busy = []
		self.count = 0

	def add_ship(self, ship):
		for d in ship.dots:
			if self.out(d) or d in self.busy:
				raise InternalExceptions()
		for d in ship.dots:
			self.field[d.x][d.y] = '■'
			self.busy.append(d)

		self.ships.append(ship)
		self.contour(ship)

	def out(self, d):
		return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

	def contour(self, ship, verb=False):
		near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
		for d in ship.dots:
			for dx, dy in near:
				cur = Dot(d.x + dx, d.y + dy)
				if not (self.out(cur)) and cur not in self.busy:
					if verb:
						self.field[cur.x][cur.y] = '.'
					self.busy.append(cur)

	def shot(self, d):
		if self.out(d):
			raise ShotBehindTheBoard()

		if d in self.busy:
			raise InTheSamePlace()

		self.busy.append(d)

		for ship in self.ships:
			if d in ship.dots:
				ship.lives -= 1
				self.field[d.x][d.y] = 'X'
				if ship.lives == 0:
					self.count += 1
					self.contour(ship, verb=True)
					print('! Корабль убит !')
					return False

				else:
					print('! Корабль ранен !')
					return True

		self.field[d.x][d.y] = '.'
		print('! Мимо !')
		return False

	def begin(self):
		self.busy = []

	def __str__(self):
		current_board = ''
		a = -1
		while a < self.size:
			a += 1
			current_board += str(a) + ' | '

		for i, row in enumerate(self.field):
			current_board += f"\n{i + 1} | " + " | ".join(row) + " |"

		if self.hid:
			current_board = current_board.replace('■', '0')

		return current_board


class Ship:
	def __init__(self, nose, length, orient):
		self.length = length
		self.nose = nose
		self.orient = orient
		self.lives = length

	@property
	def dots(self):
		ship_dots = []
		for i in range(self.length):
			cur_x = self.nose.x
			cur_y = self.nose.y

			if self.orient == 0:
				cur_x += i

			elif self.orient == 1:
				cur_y += i

			ship_dots.append(Dot(cur_x, cur_y))

		return ship_dots

	def shoot(self, shot):
		return shot in self.dots


class Player:
	def __init__(self, board, enemy):
		self.board = board
		self.enemy = enemy

	def ask(self):
		raise NotImplementedError()

	def move(self):
		while True:
			try:
				target = self.ask()
				repeat = self.enemy.shot(target)
				return repeat
			except ExceptionForTheEntireCode as e:
				print(e)


class AI(Player):
	def ask(self):
		d = Dot(randint(0, 5), randint(0, 5))
		print(f'Ход AI: {d.x+1} {d.y+1}')
		return d


class User(Player):
	def ask(self):
		while True:
			cords = input('Введите координаты: ').split()
			if len(cords) != 2:
				print('! Введена одна координата !')
				continue

			x, y = cords

			if not(x.isdigit()) or not (y.isdigit()):
				print('! Неверный ввод !')
				continue
			x, y = int(x), int(y)

			return Dot(x-1, y-1)


class Game:
	def try_board(self):
		lens = [4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1]
		board = Board(size=self.size)
		attempts = 0
		for ace in lens:
			while True:
				attempts += 1
				if attempts > 2000:
					return None
				ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), ace, randint(0, 1))
				try:
					board.add_ship(ship)
					break
				except InternalExceptions:
					pass
		board.begin()
		return board

	def random_board(self):
		board = None
		while board is None:
			board = self.try_board()
		return board

	def __init__(self, size=9):
		self.size = size
		pl = self.random_board()
		co = self.random_board()
		co.hid = False

		self.ai = AI(co, pl)
		self.us = User(pl, co)

	@staticmethod
	def greet():
		print('Морской бой\nВвод: x, y\nx - строка, y - столбец')

	def loop(self):
		num = 0
		while True:
			print('\nДоска игрока\n')
			print(self.us.board)
			print('\nДоска AI\n')
			print(self.ai.board)
			if num % 2 == 0:
				print('\nХод игрока')
				repeat = self.us.move()
			else:
				print('\nХод AI')
				repeat = self.ai.move()
			if repeat:
				num -= 1

			if self.ai.board.count == len(self.ai.board.ships):
				print('\nИгрок победил')
				break

			if self.us.board.count == len(self.us.board.ships):
				print('\nAI победил')
				break
			num += 1

	def start(self):
		self.greet()
		self.loop()


g = Game()
g.start()
