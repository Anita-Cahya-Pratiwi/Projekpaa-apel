import pygame
import random
import math
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox


# Inisialisasi Pygame
pygame.init()

# Konstanta untuk warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0,0,255)

# Konstanta untuk lebar dan tinggi jendela
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 680
MAP_SIZE = 640

# Konstanta untuk ukuran sel pada peta
CELL_SIZE = 32

# Menghitung jumlah sel horizontal dan vertikal pada peta = 20 cell
NUM_CELLS_X = MAP_SIZE // CELL_SIZE
NUM_CELLS_Y = MAP_SIZE // CELL_SIZE

num_merah = 0
MAX_MERAH = 298
list_merah = []


# Membuat jendela Pygame
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("HIDE AND SEEK KEL. APEL")
icon = pygame.image.load('miaw.jpg')
pygame.display.set_icon(icon)
cover_tombol = pygame.image.load('atascover.png')

# Kelas Peta
class Peta:
    def __init__(self):
        self.peta_data = [[0] * NUM_CELLS_X for _ in range(NUM_CELLS_Y)]
        self.obstacles = []
    
    def generate_obstacles(self, num_obstacles):
        for _ in range(num_obstacles):
            x = random.randint(0, NUM_CELLS_X - 1)
            y = random.randint(0, NUM_CELLS_Y - 1)
            # Hindari penempatan rintangan pada posisi awal pemain atau musuh
            while (x, y) == (droid_merah.x, droid_merah.y) or (x, y) == (droid_hijau.x, droid_hijau.y):
                x = random.randint(0, NUM_CELLS_X - 1)
                y = random.randint(0, NUM_CELLS_Y - 1)
            self.peta_data[y][x] = 1
            self.obstacles.append((x, y))
    
    def acak_peta(self):
        self.hapus_obstacles()  # Menghapus rintangan yang ada sebelumnya
        self.generate_obstacles(random.randint(50, 100))  # Menghasilkan rintangan baru

    def hapus_obstacles(self):
        for obstacle in self.obstacles:
            x, y = obstacle
            self.peta_data[y][x] = 0
        self.obstacles = []
    
    def is_obstacle(self, x, y):
        if x < 0 or x >= NUM_CELLS_X or y < 0 or y >= NUM_CELLS_Y:
            return True
        return self.peta_data[y][x] == 1
    
    def is_valid(self, x, y):
        return 0 <= x < NUM_CELLS_X and 0 <= y < NUM_CELLS_Y

    def draw(self):
        for y in range(NUM_CELLS_Y):
            for x in range(NUM_CELLS_X):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.is_obstacle(x, y):
                    pygame.draw.rect(window, BLACK, rect)
                else:
                    pygame.draw.rect(window, BLACK, rect, 1) 
        
    def move_droid_merah(self, new_x, new_y):
        self.droid_merah.x = new_x
        self.droid_merah.y = new_y


class Hijau:
    def __init__(self, peta):
        self.peta = peta
        self.x = random.randint(0, NUM_CELLS_X - 1)
        self.y = random.randint(0, NUM_CELLS_Y - 1)
        self.image = pygame.image.load("green.png")
        self.fov_images = [
            pygame.image.load("fov1.png"),
            pygame.image.load("fov3.png"),
            pygame.image.load("fov5.png"),
            pygame.image.load("fov7.png"),
            pygame.image.load("fov8.png")]
        
        self.current_fov_index = 0 
                
    def move(self):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if not self.peta.is_obstacle(new_x, new_y):
            self.x = new_x
            self.y = new_y          
    
    def draw(self):   
        center = (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2)
        image_rect = self.image.get_rect(center=center)
        window.blit(self.image, image_rect)
    
    def hijau_fov(self):
        hijauX = self.x * CELL_SIZE + CELL_SIZE // 2
        hijauY = self.y * CELL_SIZE + CELL_SIZE // 2
        fov_rect = self.fov_images[self.current_fov_index].get_rect()  # Mengambil gambar fov_img berdasarkan current_fov_index
        fov_rect.center = hijauX, hijauY
        window.blit(self.fov_images[self.current_fov_index], fov_rect)
        
# Kelas Pemain
class Merah:
    def __init__(self, peta):
        self.peta = peta
        self.x = random.randint(0, MAP_SIZE // CELL_SIZE - 1)
        self.y = random.randint(0, MAP_SIZE // CELL_SIZE - 1)
        self.reached_hijau = False
        self.path = []
        self.image = pygame.image.load("red.png")
            
    def move(self):
        distance = self.calculate_distance(self.x, self.y, droid_hijau.x, droid_hijau.y)     
        if distance >= 6:
            self.random_walk()

        elif distance <= 5:
            if not self.path:
                global red_sight
                self.path = self.a_star()
                droid_hijau.image.set_alpha(255)
                red_sight = False
                
            if self.path and len(self.path) > 1:
                next_x, next_y = self.path[1]
                self.x = next_x
                self.y = next_y

                # Menghapus langkah pertama dari jalur saat ditempati
                del self.path[0]
            
                # Periksa apakah tujuan akhir telah dicapai
                if self.x == droid_hijau.x and self.y == droid_hijau.y:
                    self.path = []  # Mengosongkan jalur setelah mencapai tujuan akhir

                # Periksa apakah posisi saat ini adalah rintangan
                if not peta.is_obstacle(self.x, self.y):
                    self.peta.move_droid_merah(self.x, self.y)
           
    def calculate_distance(self, x1, y1, x2, y2):
        # Euclides perhitungan jarak antara dua titik
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                
    def random_walk(self):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if not self.peta.is_obstacle(new_x, new_y):
            self.x = new_x
            self.y = new_y
                    
    def get_neighbors(self, node):
        neighbors = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x = node[0] + dx
            new_y = node[1] + dy
            if self.peta.is_valid(new_x, new_y) and not self.peta.is_obstacle(new_x, new_y):
                neighbors.append((new_x, new_y))
        return neighbors
    
    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
  
    def a_star(self):
        open_set = set([(self.x, self.y)])
        came_from = {}
        g_score = {tuple(pos): float('inf') for pos in open_set}
        g_score[(self.x, self.y)] = 0
        f_score = {tuple(pos): float('inf') for pos in open_set}
        f_score[(self.x, self.y)] = self.heuristic(self.x, self.y, droid_hijau.x, droid_hijau.y)

        while open_set:
            current = min(open_set, key=lambda pos: f_score[pos])

            if current == (droid_hijau.x, droid_hijau.y):
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor[0], neighbor[1], droid_hijau.x, droid_hijau.y)
                    if neighbor not in open_set:
                        open_set.add(neighbor)

        return None
    
    def heuristic(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def draw(self):
        center = (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2)
        image_rect = self.image.get_rect(center=center)
        window.blit(self.image, image_rect)
        

"FUNGSI-FUNGSI UNTUK TOMBOL FITUR"
# Fungsi untuk memulai
def start_game():
    global game_started
    game_started = True

# Fungsi untuk jeda
def pause():
    global game_paused
    game_paused = not game_paused

# Random Start Red
def random_start_red():
    global droid_merah
    droid_merah = Merah(peta)

# Random Start Green
def random_start_green():
    global droid_hijau
    droid_hijau = Hijau(peta)
   
#Tambah droid merah
def add_merah():
    global num_merah
    if num_merah < MAX_MERAH:
        valid_position = False
        while not valid_position:
            new_x = random.randint(0, len(peta.peta_data[0]) - 1)
            new_y = random.randint(0, len(peta.peta_data) - 1)
            if not peta.is_obstacle(new_x, new_y):
                valid_position = True
        new_merah = Merah(peta)  
        new_merah.x = new_x
        new_merah.y = new_y
        list_merah.append(new_merah)
        num_merah += 1        
        
#kurangi        
def kurangi_merah():
    global num_merah
    if num_merah > 0:
        list_merah.pop()
        num_merah -= 1
        
def pandangan_merah():
    global red_sight
    red_sight = True   

def pandangan_hijau():
    global green_sight
    green_sight = True   

def normal():
    global green_sight, red_sight
    green_sight = False
    red_sight = False
        
        
        
"TOMBOL MULAI"
Mulai = Button(
        window, 740, 10, 100, 40,
        text='Start',
        textColour=(250,250,250),
        fontSize=25,
        margin=20,
        radius=20,
        onClick= lambda: start_game())
"TOMBOL JEDA ATAU LANJUTKAN"
Jeda = Button(
        window, 740, 70, 200, 40,
        text='Pause or Continue',
        textColour=(250,250,250),
        fontSize=25,
        margin=20,
        radius=20, 
        onClick= lambda: pause())
Acak_peta = Button(
        window, 740, 130, 100, 40,
        text='Random Map',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: peta.acak_peta())
Acak_merah = Button(
        window, 740, 190, 150, 40,
        text='Random Start Red',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: random_start_red())
Acak_hijau = Button(
        window, 740, 250, 150, 40,
        text='Random Start Green',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: random_start_green())
Tambahkan_merah = Button(
        window, 740, 310, 150, 40,
        text='Add More Red Droid',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: add_merah())
Hapus_merah = Button(
        window,740, 370, 100, 40,
        text='Remove Red',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: kurangi_merah())
merah_sight= Button(
        window,740, 370, 100, 40,
        text='Red Sight',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: 
        pandangan_merah())
hijau_sight = Button(
        window, 740, 430, 100, 40,
        text='Green Sight',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: 
        pandangan_hijau())
pengaturan = Button(
        window, 780, 510, 200, 40,
        text='SETTING GREEN SIGHT',
        fontSize=20,
        margin=20,
        inactiveColour=(250, 250, 250),
        hoverColour=(250, 250, 250),
        pressedColour=(250, 250, 250))
kurangi_red = Button(
        window, 740, 560, 100, 40,
        text='Kurangi Merah',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: 
        kurangi_merah())
normal_pandang = Button(
        window, 740, 610, 100, 40,
        text='Normal Sight',
        textColour=(250,250,250),
        fontSize=20,
        margin=20,
        radius=20,
        onClick=lambda: 
        normal())

slider = Slider(window, 740, 490, 230, 10, min=1, max=5, step=1)
output = TextBox(window, 740, 510, 40, 40, fontSize=25)
output.disable()


game_started = False
game_paused = False
red_sight = False
green_sight = False
    
# Inisialisasi peta dan pemain
peta = Peta()
droid_merah = Merah(peta)
peta.droid_merah = droid_merah
droid_hijau = Hijau(peta)
peta.generate_obstacles(random.randint(50,100))

# agar merah tidak start di wall
while peta.is_obstacle(droid_merah.x, droid_merah.y):
    droid_merah = Merah(peta)
    peta.droid_merah = droid_merah
# agar hijau tidak start di wall
while peta.is_obstacle(droid_hijau.x, droid_hijau.y) or (droid_hijau.x, droid_hijau.y) == (droid_merah.x, droid_merah.y):
    droid_hijau = Hijau(peta)
    peta.droid_merah = droid_merah

# Mengatur Clock untuk mengatur FPS
clock = pygame.time.Clock()
FPS = 2

# Loop Utama
running = True
while running:
    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
            quit()
         
    # Menggambar latar belakang
    window.fill(WHITE)
    
    # Menggambar peta dan pemain
    peta.draw()
    
    if green_sight and not red_sight:    
        droid_hijau.hijau_fov()
        
    droid_hijau.draw()
    
    if not red_sight :
        droid_hijau.image.set_alpha(255)
    elif red_sight and not green_sight:
        droid_hijau.image.set_alpha(0)
        
    droid_merah.draw()
    for droid in list_merah:
        droid.draw() 
    
    # Mendapatkan nilai dari tombol slider
    # Mengurangi 1 untuk mengakses indeks dalam daftar fov_images
    current_fov_index = slider.getValue() - 1  
    droid_hijau.current_fov_index = current_fov_index
      
    if game_started and not game_paused:
    # Memeriksa apakah pemain mencapai target musuh
        distance = droid_merah.calculate_distance(droid_merah.x, droid_merah.y, droid_hijau.x, droid_hijau.y)         
        if distance == 0 and droid_merah.x == droid_hijau.x and droid_merah.y == droid_hijau.y:
           reached_hijau = True
           game_started = False
       
        if not droid_merah.reached_hijau:
            droid_merah.move()
            droid_hijau.move()            
            for droid_merah in list_merah:
                droid_merah.move() 
        
    window.blit(cover_tombol, (0,0))        
    pygame_widgets.update(events)
    output.setText(str(slider.getValue()))
    pygame.display.update()

    # Mengatur FPS
    clock.tick(FPS)
