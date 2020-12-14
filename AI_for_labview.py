from random import randint

HEIGHT = 35
WIDTH = 25
FIELD_SIZE = HEIGHT * WIDTH
 
HEAD = 0

FOOD = 0
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)
SNAKE = 2 * UNDEFINED

LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH
 

ERR = -1111

board = [0] * FIELD_SIZE
snake = [0] * (FIELD_SIZE+1)
snake_size = 8
snake[HEAD] = 1*WIDTH+1

tmpboard = [0] * FIELD_SIZE
tmpsnake = [0] * (FIELD_SIZE+1)
tmpsnake_size = 8
tmpsnake[HEAD] = 1*WIDTH+1

food = 3 * WIDTH + 3
best_move = ERR
 

mov = [LEFT, RIGHT, UP, DOWN]
                                                  
score = 1 
 

def is_cell_free(idx, psize, psnake):
    return not (idx in psnake[:psize]) 
 

def is_move_possible(idx, move):
    flag = False
    if move == LEFT:
        flag = True if idx%WIDTH > 1 else False
    elif move == RIGHT:
        flag = True if idx%WIDTH < (WIDTH-2) else False
    elif move == UP:
        flag = True if idx > (2*WIDTH-1) else False 
    elif move == DOWN:
        flag = True if idx < (FIELD_SIZE-2*WIDTH) else False 
    return flag

def board_reset(psnake, psize, pboard):
    for i in range(FIELD_SIZE):
        if i == food:
            pboard[i] = FOOD
        elif is_cell_free(i, psize, psnake): 
            pboard[i] = UNDEFINED
        else: 
            pboard[i] = SNAKE
     

def board_refresh(pfood, psnake, pboard):
    queue = []
    queue.append(pfood)
    inqueue = [0] * FIELD_SIZE
    found = False
   
    while len(queue)!=0: 
        idx = queue.pop(0)
        if inqueue[idx] == 1: continue
        inqueue[idx] = 1
        for i in range(4):
            if is_move_possible(idx, mov[i]):
                if idx + mov[i] == psnake[HEAD]:
                    found = True
                if pboard[idx+mov[i]] < SNAKE: 
                     
                    if pboard[idx+mov[i]] > pboard[idx]+1:
                        pboard[idx+mov[i]] = pboard[idx] + 1
                    if inqueue[idx+mov[i]] == 0:
                        queue.append(idx+mov[i])
 
    return found
 

def choose_shortest_safe_move(psnake, pboard):
    best_move = ERR
    min = SNAKE
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<min:
            min = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move
 

def choose_longest_safe_move(psnake, pboard):
    best_move = ERR
    max = -1
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<UNDEFINED and pboard[psnake[HEAD]+mov[i]]>max:
            max = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move
 

def is_tail_inside():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size-1]] = 0 
    result = board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) 
    for i in range(4): 
        if is_move_possible(tmpsnake[HEAD], mov[i]) and tmpsnake[HEAD]+mov[i]==tmpsnake[tmpsnake_size-1] and tmpsnake_size>3:
            result = False
    return result
 

def follow_tail():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard) 
    tmpboard[tmpsnake[tmpsnake_size-1]] = FOOD 
    tmpboard[food] = SNAKE 
    board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) 
    tmpboard[tmpsnake[tmpsnake_size-1]] = SNAKE 
 
    return choose_longest_safe_move(tmpsnake, tmpboard)
def any_possible_move():
    global food , snake, snake_size, board
    best_move = ERR
    board_reset(snake, snake_size, board)
    board_refresh(food, snake, board)
    min = SNAKE
 
    for i in range(4):
        if is_move_possible(snake[HEAD], mov[i]) and board[snake[HEAD]+mov[i]]<min:
            min = board[snake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move
 
def shift_array(arr, size):
    for i in range(size, 0, -1):
        arr[i] = arr[i-1]
 
def new_food():
    global food, snake_size
    cell_free = False
    while not cell_free:
        w = randint(1, WIDTH-2)
        h = randint(1, HEIGHT-2)
        food = h * WIDTH + w
        cell_free = is_cell_free(food, snake_size, snake)
        print("snake size is now up to : " +str(snake_size))
        print("next food : "+str(int(food/WIDTH))+","+str(food%WIDTH))

  
def make_move(pbest_move):
    global  snake, board, snake_size, score
    shift_array(snake, snake_size)
    snake[HEAD] += pbest_move
    
    print(str(int(snake[HEAD]/WIDTH))+","+str(snake[HEAD]%WIDTH)) 
 

    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE 
        snake_size += 1
        score += 1
        if snake_size < FIELD_SIZE: new_food()
    else: 
        board[snake[HEAD]] = SNAKE 
        board[snake[snake_size]] = UNDEFINED 
 

def virtual_shortest_move():
    global snake, board, snake_size, tmpsnake, tmpboard, tmpsnake_size, food
    tmpsnake_size = snake_size
    tmpsnake = snake[:] 
    tmpboard = board[:] 
    board_reset(tmpsnake, tmpsnake_size, tmpboard)
     
    food_eated = False
    while not food_eated:
        board_refresh(food, tmpsnake, tmpboard)    
        move = choose_shortest_safe_move(tmpsnake, tmpboard)
        shift_array(tmpsnake, tmpsnake_size)
        tmpsnake[HEAD] += move
        if tmpsnake[HEAD] == food:
            tmpsnake_size += 1
            board_reset(tmpsnake, tmpsnake_size, tmpboard) 
            tmpboard[food] = SNAKE
            food_eated = True
        else: 
            tmpboard[tmpsnake[HEAD]] = SNAKE
            tmpboard[tmpsnake[tmpsnake_size]] = UNDEFINED
 
def find_safe_way():
    global snake, board
    safe_move = ERR
    virtual_shortest_move()
    if is_tail_inside(): 
        return choose_shortest_safe_move(snake, board)
    safe_move = follow_tail() 
    return safe_move

     

def main(food, snake):
    board_reset(snake, snake_size, board)
    if board_refresh(food, snake, board):
        best_move  = find_safe_way() 
    else:
        best_move = follow_tail()
             
    if best_move == ERR:
        best_move = any_possible_move()

    if best_move != ERR: 
        make_move(best_move) 
    return snake
         