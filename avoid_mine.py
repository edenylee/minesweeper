import pygame as pg
import random
import sys
import time

background_color = ( 50,  50,  50)
black            = (  0,   0,   0)
white            = (255, 255, 255)
dark_white       = (235, 235, 235)
cyan             = (100, 180, 255)
green            = ( 51, 204,   0)
blue             = (  0,   0, 255)
red              = (255,   0,   0)
yellow           = (255, 255,   0)
pink             = (255,  51, 204)

margin = 100
cell_size = 40
cell_num = 15
screen_size = [margin*2 + cell_size*cell_num, margin*2 + cell_size*cell_num]
initial_cells = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
initial_mine_cells = [(0, 1), (1, 0), (1, 1)]

fps = 60
clock = pg.time.Clock()

def main():
    pg.init()
    screen = pg.display.set_mode(screen_size)
    pg.display.set_caption("지뢰피하기")

    game = Game(screen)
    button = Button(screen, game)

    while True:
        button.check_click()

def play_game(screen, game, level, button):
    screen.fill(background_color)
    game.init_game(level)

    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                pressed = pg.key.get_pressed()
                keynames = [pg.key.name(key) for key, value in enumerate(pressed) if value]
                game.check_keypress(keynames)

            elif event.type == pg.QUIT:
                game.exit()

        if game.is_fail:
            return game.is_fail

        if game.is_success:
            return game.is_success
        
        pg.display.flip()
        clock.tick(fps)

def print_text(font, screen, msg, color, pos):
    textSurface = font.render(msg, True, color, None)
    textRect = textSurface.get_rect()
    textRect.center = pos
    screen.blit(textSurface, textRect)
    return textRect

class Game(object):
    def __init__(self, screen):
        self.screen = screen
        self.font = pg.font.SysFont("Times New Roman", margin*3//10)
        self.font2 = pg.font.SysFont("새굴림", margin*3//10)

    def init_game(self, level):
        self.coordinate = [[0 for y in range(cell_num)] for x in range(cell_num)]
        self.mine_coordinate = [[0 for y in range(cell_num)] for x in range(cell_num)]
        self.current_coordinate = [0, 0]
        self.secured_coordinate = [(0, 0)]
        self.show_list = [x for x in initial_cells]
        self.showed_list = []
        self.block_list = {}
        self.is_fail = False
        self.is_success = False
        self.set_path()
        self.set_mines(level)
        self.draw_secured_cells()
        self.draw_board()
        self.show_numbers()
        self.draw_me()

    def draw_board(self):
        for i in range(cell_num+1):
            pg.draw.aaline(self.screen, white, [margin, margin + cell_size*i], [margin + cell_size*cell_num, margin + cell_size*i])
            pg.draw.aaline(self.screen, white, [margin + cell_size*i, margin], [margin + cell_size*i, margin + cell_size*cell_num])

    def check_keypress(self, keynames):
        for key in keynames:
            if key == "R" and self.current_coordinate[1] > 0:
                self.current_coordinate[1] -= 1
                self.is_fail = self.secure_cell()
            elif key == "Q" and self.current_coordinate[1] < cell_num-1:
                self.current_coordinate[1] += 1
                self.is_fail = self.secure_cell()
            elif key == "P" and self.current_coordinate[0] > 0:
                self.current_coordinate[0] -= 1
                self.is_fail = self.secure_cell()
            elif key == "O" and self.current_coordinate[0] < cell_num-1:
                self.current_coordinate[0] += 1
                self.is_fail = self.secure_cell()
        
        if self.current_coordinate[0] == cell_num-1 and self.current_coordinate[1] == cell_num-1:
            self.is_success = True

    def draw_secured_cells(self):
        for x, y in self.secured_coordinate:
            pg.draw.rect(self.screen, dark_white, [margin + cell_size*x, margin + cell_size*y, cell_size, cell_size])
        pg.draw.rect(self.screen, yellow, [margin + cell_size*(cell_num-1), margin + cell_size*(cell_num-1), cell_size, cell_size])

    def show_numbers(self):
        for x, y in self.secured_coordinate:
            if y > 0 and (x, y-1) not in self.show_list: # 상
                self.show_list.append((x, y-1))
            if y < cell_num-1 and (x, y+1) not in self.show_list: # 하
                self.show_list.append((x, y+1))
            if x > 0 and (x-1, y) not in self.show_list: # 좌
                self.show_list.append((x-1, y))
            if x < cell_num-1 and (x+1, y) not in self.show_list: # 우
                self.show_list.append((x+1, y))
            if x > 0 and y > 0 and (x-1, y-1) not in self.show_list: # 좌상
                self.show_list.append((x-1, y-1))
            if x > 0 and y < cell_num-1 and (x-1, y+1) not in self.show_list: # 좌하
                self.show_list.append((x-1, y+1))
            if x < cell_num-1 and y > 0 and (x+1, y-1) not in self.show_list: # 우상
                self.show_list.append((x+1, y-1))
            if x < cell_num-1 and y < cell_num-1 and (x+1, y+1) not in self.show_list: # 우하
                self.show_list.append((x+1, y+1))

        for x, y in self.show_list:
            value = self.coordinate[y][x]
            text = str(value)
            if value != "M" and value != cell_num**2-1:
                if (x, y) not in self.showed_list or (x, y) in self.secured_coordinate:
                    self.showed_list.append((x, y))
                    if self.mine_coordinate[y][x] == "홀" or self.mine_coordinate[y][x] == "짝":
                        msg = self.mine_coordinate[y][x]
                        print_text(self.font2, self.screen, msg, pink,\
                                    (margin + cell_size//2 + cell_size*x, margin + cell_size//2 + cell_size*y))
      
                    else:
                        msg = text
                        if value < 3:
                            print_text(self.font, self.screen, msg, blue,\
                                        (margin + cell_size//2 + cell_size*x, margin + cell_size//2 + cell_size*y))
                        elif value < 5:
                            print_text(self.font, self.screen, msg, green,\
                                        (margin + cell_size//2 + cell_size*x, margin + cell_size//2 + cell_size*y))
                        else:
                            print_text(self.font, self.screen, msg, red,\
                                        (margin + cell_size//2 + cell_size*x, margin + cell_size//2 + cell_size*y))

            bomb_img = pg.image.load("bomb.png")
            bomb = pg.transform.scale(bomb_img, (cell_size, cell_size))
        for x, y in initial_mine_cells:
            if self.mine_coordinate[y][x] == "M":
                self.screen.blit(bomb, (margin + cell_size*x, margin + cell_size*y))

    def draw_me(self):
        pg.draw.rect(self.screen, cyan, [margin + cell_size//8 + cell_size*self.current_coordinate[0],\
                                    margin + cell_size//8 + cell_size*self.current_coordinate[1],\
                                    (cell_size*3)//4, (cell_size*3)//4])

    def secure_cell(self):
        if self.mine_coordinate[self.current_coordinate[1]][self.current_coordinate[0]] == "M": # 지뢰칸을 밟았는지 먼저 검사
            bomb_img = pg.image.load("bomb.png")
            bomb = pg.transform.scale(bomb_img, (cell_size, cell_size))
            for x in range(cell_num):
                for y in range(cell_num):
                    if self.mine_coordinate[y][x] == "M":
                        pg.draw.rect(self.screen, red, [margin + cell_size*x, margin + cell_size*y, cell_size, cell_size])
                        self.screen.blit(bomb, (margin + cell_size*x, margin + cell_size*y))
            self.draw_board()
            return True

        if (self.current_coordinate[0], self.current_coordinate[1]) not in self.secured_coordinate:
            self.secured_coordinate.append((self.current_coordinate[0], self.current_coordinate[1]))
        
        if (self.current_coordinate[0], self.current_coordinate[1]) in self.showed_list:
            self.showed_list.remove((self.current_coordinate[0], self.current_coordinate[1]))

        self.draw_secured_cells()
        self.draw_board()
        self.show_numbers()
        self.draw_me()
        return False

    def set_path(self):
        x, y = 0, 0
        while x+y < (cell_num-1)*2:
            if random.random() > 0.5 and x < cell_num-1:
                x += 1
                self.mine_coordinate[y][x] = "P"
            elif y < cell_num-1:
                y += 1
                self.mine_coordinate[y][x] = "P"

    def set_mines(self, level):
        if level == "easy":
            mine_num = (cell_num**2)//5
        elif level == "normal":
            mine_num = (cell_num**2)//3
        elif level == "hard" or "lunatic":
            mine_num = (cell_num**2)//2

        minefield = list(range(1, cell_num**2))
        for mine in range(1, cell_num**2):
            if self.mine_coordinate[mine//cell_num][mine%cell_num] == "P":
                minefield.remove(mine)
        mine_list = random.sample(minefield, mine_num)
        for mine in mine_list:
            mine_X = mine%cell_num
            mine_Y = mine//cell_num
            self.mine_coordinate[mine_Y][mine_X] = "M"

            self.coordinate[mine_Y][mine_X] += 1 # 지뢰가 있는 칸
            if mine_Y > 0: # 상
                self.coordinate[mine_Y - 1][mine_X] += 1
            if mine_Y < cell_num-1: # 하
                self.coordinate[mine_Y + 1][mine_X] += 1
            if mine_X > 0: # 좌
                self.coordinate[mine_Y][mine_X - 1] += 1
            if mine_X < cell_num-1: # 우
                self.coordinate[mine_Y][mine_X + 1] += 1
            if mine_Y > 0 and mine_X > 0: # 좌상
                self.coordinate[mine_Y - 1][mine_X - 1] += 1
            if mine_Y < cell_num-1 and mine_X > 0: # 좌하
                self.coordinate[mine_Y + 1][mine_X - 1] += 1
            if mine_Y > 0 and mine_X < cell_num-1: # 우상
                self.coordinate[mine_Y - 1][mine_X + 1] += 1
            if mine_Y < cell_num-1 and mine_X < cell_num-1: # 우하
                self.coordinate[mine_Y + 1][mine_X + 1] += 1

        for i in range(5): # 3칸 이상의 갈 수 없는 인접한 블록을 찾아 갈 수 있도록 연결
            self.block_list = {}
            self.search_blocks()

            if len(self.block_list) > 1:
                deleted_cells = self.link_blocks()
                if deleted_cells:
                    for cell in deleted_cells:
                        self.mine_coordinate[cell//cell_num][cell%cell_num] = 0
        
        self.delete_9nines_blocks() # 지뢰매설량이 9인 칸이 있을 경우 자신 포함 주변 9칸 중 한 칸의 지뢰 제거
        self.reduce_zeros(level) # easy/normal의 경우 지뢰매설량 0인 칸 하나에 지뢰 추가, hard/lunatic의 경우 지뢰매설량이 0인 칸이 없을 때까지 지뢰 추가

        if level == "lunatic":
            count = 0
            while count < cell_num:
                for i in range(cell_num**2):
                    if random.random() > 0.95:
                        if self.mine_coordinate[i//cell_num][i%cell_num] == 0:
                            if self.coordinate[i//cell_num][i%cell_num] % 2 == 0: self.mine_coordinate[i//cell_num][i%cell_num] = "짝"
                            else: self.mine_coordinate[i//cell_num][i%cell_num] = "홀"
                            count += 1

    def search_blocks(self):
        self.num_list = [x for x in range(cell_num**2)]
        count = 0
        while count < cell_num**2:
            if count in self.num_list and self.mine_coordinate[count//cell_num][count%cell_num] != "M":
                self.num_list.remove(count)
                self.block_list[count] = [count]
                self.search_blanks(count, count, self.mine_coordinate)
            count += 1
            
    def search_blanks(self, count, index, coord):
        if count%cell_num != 0 and coord[(count-1)//cell_num][(count-1)%cell_num] != "M" and count-1 in self.num_list:
            self.block_list[index].append(count-1)
            self.num_list.remove(count-1)
            self.search_blanks(count-1, index, coord)

        if count%cell_num != cell_num-1 and coord[(count+1)//cell_num][(count+1)%cell_num] != "M" and count+1 in self.num_list:
            self.block_list[index].append(count+1)
            self.num_list.remove(count+1)
            self.search_blanks(count+1, index, coord)

        if count//cell_num != 0 and coord[(count-cell_num)//cell_num][(count-cell_num)%cell_num] != "M" and count-cell_num in self.num_list:
            self.block_list[index].append(count-cell_num)
            self.num_list.remove(count-cell_num)
            self.search_blanks(count-cell_num, index, coord)

        if count//cell_num != cell_num-1 and coord[(count+cell_num)//cell_num][(count+cell_num)%cell_num] != "M" and count+cell_num in self.num_list:
            self.block_list[index].append(count+cell_num)
            self.num_list.remove(count+cell_num)
            self.search_blanks(count+cell_num, index, coord)

    def link_blocks(self):
        link_list = {}
        for block in self.block_list:
            if block != 0:
                link_list[block] = []
                for path_cell in self.block_list[0]:
                    for this_cell in self.block_list[block]:
                        this_X = this_cell%cell_num
                        this_Y = this_cell//cell_num
                        if this_Y >= 2 and path_cell == this_cell - cell_num*2:
                            if this_cell-cell_num not in link_list[block]: link_list[block].append(this_cell-cell_num)
                        if this_Y <= cell_num-3 and path_cell == this_cell + cell_num*2:
                            if this_cell+cell_num not in link_list[block]: link_list[block].append(this_cell+cell_num)
                        if this_X >= 2 and path_cell == this_cell - 2:
                            if this_cell-1 not in link_list[block]: link_list[block].append(this_cell-1)
                        if this_X <= cell_num-3 and path_cell == this_cell + 2:
                            if this_cell+1 not in link_list[block]: link_list[block].append(this_cell+1)
                        if this_Y >= 1 and this_X >= 1 and path_cell == this_cell - (cell_num + 1):
                            if this_cell-cell_num not in link_list[block]: link_list[block].append(this_cell-cell_num)
                            if this_cell-1 not in link_list[block]: link_list[block].append(this_cell-1)
                        if this_Y >= 1 and this_X <= cell_num-3 and path_cell == this_cell - (cell_num - 1):
                            if this_cell-cell_num not in link_list[block]: link_list[block].append(this_cell-cell_num)
                            if this_cell+1 not in link_list[block]: link_list[block].append(this_cell+1)
                        if this_Y <= cell_num-3 and this_X >= 1 and path_cell == this_cell - (-cell_num + 1):
                            if this_cell+cell_num not in link_list[block]: link_list[block].append(this_cell+cell_num)
                            if this_cell-1 not in link_list[block]: link_list[block].append(this_cell-1)
                        if this_Y <= cell_num-3 and this_X <= cell_num-3 and path_cell == this_cell - (-cell_num - 1):
                            if this_cell+cell_num not in link_list[block]: link_list[block].append(this_cell+cell_num)
                            if this_cell+1 not in link_list[block]: link_list[block].append(this_cell+1)
        
        new_link_list = [random.choice(link_list[x]) for x in link_list if link_list[x] and len(self.block_list[x]) > 2]

        if 0 < len(new_link_list) < 3:
            return random.sample(new_link_list, 1)
        elif len(new_link_list) >= 3:
            return random.sample(new_link_list, len(new_link_list)-1)
        return False

    def delete_9nines_blocks(self):
        for y in range(cell_num):
            for x in range(cell_num):
                if self.coordinate[y][x] == 9:
                    random_x = random.choice(range(-1, 2, 1))
                    random_y = random.choice(range(-1, 2, 1))
                    self.mine_coordinate[y+random_y][x+random_x] = 0
                    self.coordinate[y+random_y][x+random_x-1] -= 1
                    if x+random_x > 0: self.coordinate[y+random_y][x+random_x-1] -= 1
                    if x+random_x < cell_num-1: self.coordinate[y+random_y][x+random_x+1] -= 1
                    if y+random_y > 0: self.coordinate[y+random_y-1][x+random_x] -= 1
                    if y+random_y < cell_num-1: self.coordinate[y+random_y+1][x+random_x] -= 1
                    if x+random_x > 0 and y+random_y > 0: self.coordinate[y+random_y-1][x+random_x-1] -= 1
                    if x+random_x < cell_num-1 and y+random_y > 0: self.coordinate[y+random_y-1][x+random_x+1] -= 1
                    if x+random_x > 0 and y+random_y < cell_num-1: self.coordinate[y+random_y+1][x+random_x-1] -= 1
                    if x+random_x < cell_num-1 and y+random_y < cell_num-1: self.coordinate[y+random_y+1][x+random_x+1] -= 1

    def reduce_zeros(self, level):
        if level == "easy" or level == "normal":
            zero_count = 0
            zero_list = []
            zero = None
            for y in range(cell_num):
                for x in range(cell_num):
                    if self.coordinate[y][x] == 0 and (x, y) != (0, 0) and (x, y) != (cell_num-1, cell_num-1):
                        zero_count += 1
                        zero_list.append((x, y))
            if zero_count > 0:
                zero = random.choice(zero_list)
                self.mine_coordinate[zero[1]][zero[0]] = "M"
                self.coordinate[zero[1]][zero[0]] += 1
                if zero[0] > 0: self.coordinate[zero[1]][zero[0]-1] += 1
                if zero[0] < cell_num-1: self.coordinate[zero[1]][zero[0]+1] += 1
                if zero[1] > 0: self.coordinate[zero[1]-1][zero[0]] += 1
                if zero[1] < cell_num-1: self.coordinate[zero[1]+1][zero[0]] += 1
                if zero[0] > 0 and zero[1] > 0: self.coordinate[zero[1]-1][zero[0]-1] += 1
                if zero[0] < cell_num-1 and zero[1] > 0: self.coordinate[zero[1]-1][zero[0]+1] += 1
                if zero[0] > 0 and zero[1] < cell_num-1: self.coordinate[zero[1]+1][zero[0]-1] += 1
                if zero[0] < cell_num-1 and zero[1] < cell_num-1: self.coordinate[zero[1]+1][zero[0]+1] += 1
        else:
            switch = True
            while switch:
                zero_count = 0
                zero_list = []
                zero = None
                for y in range(cell_num):
                    for x in range(cell_num):
                        if self.coordinate[y][x] == 0 and (x, y) != (0, 0) and (x, y) != (cell_num-1, cell_num-1):
                            zero_count += 1
                            zero_list.append((x, y))

                if zero_count > 0:
                    zero = random.choice(zero_list)
                    self.mine_coordinate[zero[1]][zero[0]] = "M"
                    self.coordinate[zero[1]][zero[0]] += 1
                    if zero[0] > 0: self.coordinate[zero[1]][zero[0]-1] += 1
                    if zero[0] < cell_num-1: self.coordinate[zero[1]][zero[0]+1] += 1
                    if zero[1] > 0: self.coordinate[zero[1]-1][zero[0]] += 1
                    if zero[1] < cell_num-1: self.coordinate[zero[1]+1][zero[0]] += 1
                    if zero[0] > 0 and zero[1] > 0: self.coordinate[zero[1]-1][zero[0]-1] += 1
                    if zero[0] < cell_num-1 and zero[1] > 0: self.coordinate[zero[1]-1][zero[0]+1] += 1
                    if zero[0] > 0 and zero[1] < cell_num-1: self.coordinate[zero[1]+1][zero[0]-1] += 1
                    if zero[0] < cell_num-1 and zero[1] < cell_num-1: self.coordinate[zero[1]+1][zero[0]+1] += 1
                else:
                    switch = False

    def exit(self):
        pg.quit()
        sys.exit()

class Button(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.font = pg.font.SysFont("Times New Roman", margin*3//10)
        self.font2 = pg.font.SysFont("새굴림", margin*3//10)
        self.game = game
        self.draw_buttons()

    def draw_buttons(self):
        first_X = margin + cell_size
        first_Y = (margin*3)//2 + cell_size*cell_num
        easy_rect = print_text(self.font, self.screen, "Easy", blue, (first_X, first_Y))
        normal_rect = print_text(self.font, self.screen, "Normal", green, (first_X + cell_num*10, first_Y))
        hard_rect = print_text(self.font, self.screen, "Hard", red, (first_X + cell_num*20, first_Y))
        lunatic_rect = print_text(self.font, self.screen, "Lunatic", yellow, (first_X + cell_num*30, first_Y))
        self.rects = [easy_rect, normal_rect, hard_rect, lunatic_rect]
        return self.rects

    def check_click(self):
        fail = False
        while True:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.check_button(event.pos):
                        level = self.check_button(event.pos)
                        fail = play_game(self.screen, self.game, level, self)
                elif event.type == pg.QUIT:
                    self.game.exit()
        
            if fail:
                if self.game.is_fail:
                    self.show_msg("lose")
                    self.draw_buttons()
                    return
                elif self.game.is_success:
                    self.show_msg("win")
                    self.draw_buttons()
                    return
            pg.display.flip()
            clock.tick(fps)

    def check_button(self, pos):
        if self.rects[0].collidepoint(pos):
            level = "easy"
            return level
        elif self.rects[1].collidepoint(pos):
            level = "normal"
            return level
        elif self.rects[2].collidepoint(pos):
            level = "hard"
            return level
        elif self.rects[3].collidepoint(pos):
            level = "lunatic"
            return level
        return False
    
    def show_msg(self, sort):
        msg = {"win"   : ["Win!!", yellow],
               "lose"  : ["Lose..", red]}
        print_text(self.font, self.screen, msg[sort][0], msg[sort][1], (margin + cell_size*cell_num//2, margin//2))

main()