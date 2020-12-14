import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
 
# 蛇運動的場地長寬
HEIGHT = 35
WIDTH = 25
FIELD_SIZE = HEIGHT * WIDTH
 
# 蛇頭總是位於snake陣列的第一個元素
HEAD = 0
 
# 用來代表不同東西的數字，由於矩陣上每個格子會處理成到達食物的路徑長度，
# 因此這三個變數間需要有足夠大的間隔(>HEIGHT*WIDTH)
FOOD = 0
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)
SNAKE = 2 * UNDEFINED
 
# 由於snake是一維陣列，所以對應元素直接加上以下值就表示向四個方向移動
LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH
 
# 錯誤碼
ERR = -1111
 
# 用一維陣列來表示二維的東西
# board表示蛇運動的矩形場地
# 初始化蛇頭在(1,1)的地方，第0行，HEIGHT行，第0列，WIDTH列為圍牆，不可用
# 初始蛇長度為1
board = [0] * FIELD_SIZE
snake = [0] * (FIELD_SIZE+1)
snake_size = 8
snake[HEAD] = 1*WIDTH+1
# 與上面變數對應的臨時變數，蛇試探性地移動時使用
tmpboard = [0] * FIELD_SIZE
tmpsnake = [0] * (FIELD_SIZE+1)
tmpsnake_size = 8
tmpsnake[HEAD] = 1*WIDTH+1
# food:食物位置(0~FIELD_SIZE-1),初始在(3, 3)
# best_move: 運動方向
food = 3 * WIDTH + 3
best_move = ERR
 
# 運動方向陣列
mov = [LEFT, RIGHT, UP, DOWN]
# 接收到的鍵 和 分數
key = KEY_RIGHT                                                    
score = 1 #分數也表示蛇長
 
# 檢查一個cell有沒有被蛇身覆蓋，沒有覆蓋則為free，返回true
def is_cell_free(idx, psize, psnake):
    return not (idx in psnake[:psize]) 
 
# 檢查某個位置idx是否可向move方向運動
def is_move_possible(idx, move):
    flag = False
    if move == LEFT:
        flag = True if idx%WIDTH > 1 else False
    elif move == RIGHT:
        flag = True if idx%WIDTH < (WIDTH-2) else False
    elif move == UP:
        flag = True if idx > (2*WIDTH-1) else False # 即idx/WIDTH > 1
    elif move == DOWN:
        flag = True if idx < (FIELD_SIZE-2*WIDTH) else False # 即idx/WIDTH < HEIGHT-2
    return flag
# 重置board
# board_refresh後，UNDEFINED值都變為了到達食物的路徑長度
# 如需要還原，則要重置它
def board_reset(psnake, psize, pboard):
    for i in range(FIELD_SIZE):
        if i == food:
            pboard[i] = FOOD
        elif is_cell_free(i, psize, psnake): # 該位置為空
            pboard[i] = UNDEFINED
        else: # 該位置為蛇身
            pboard[i] = SNAKE
     
# 廣度優先搜尋遍歷整個board，
# 計算出board中每個非SNAKE元素到達食物的路徑長度
def board_refresh(pfood, psnake, pboard):
    queue = []
    queue.append(pfood)
    inqueue = [0] * FIELD_SIZE
    found = False
    # while迴圈結束後，除了蛇的身體，
    # 其它每個方格中的數字程式碼從它到食物的路徑長度
    while len(queue)!=0: 
        idx = queue.pop(0)
        if inqueue[idx] == 1: continue
        inqueue[idx] = 1
        for i in range(4):
            if is_move_possible(idx, mov[i]):
                if idx + mov[i] == psnake[HEAD]:
                    found = True
                if pboard[idx+mov[i]] < SNAKE: # 如果該點不是蛇的身體
                     
                    if pboard[idx+mov[i]] > pboard[idx]+1:
                        pboard[idx+mov[i]] = pboard[idx] + 1
                    if inqueue[idx+mov[i]] == 0:
                        queue.append(idx+mov[i])
 
    return found
 
# 從蛇頭開始，根據board中元素值，
# 從蛇頭周圍4個領域點中選擇最短路徑
def choose_shortest_safe_move(psnake, pboard):
    best_move = ERR
    min = SNAKE
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<min:
            min = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move
 
# 從蛇頭開始，根據board中元素值，
# 從蛇頭周圍4個領域點中選擇最遠路徑
def choose_longest_safe_move(psnake, pboard):
    best_move = ERR
    max = -1
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<UNDEFINED and pboard[psnake[HEAD]+mov[i]]>max:
            max = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move
 
# 檢查是否可以追著蛇尾運動，即蛇頭和蛇尾間是有路徑的
# 為的是避免蛇頭陷入死路
# 虛擬操作，在tmpboard,tmpsnake中進行
def is_tail_inside():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size-1]] = 0 # 虛擬地將蛇尾變為食物(因為是虛擬的，所以在tmpsnake,tmpboard中進行)
    tmpboard[food] = SNAKE # 放置食物的地方，看成蛇身
    result = board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # 求得每個位置到蛇尾的路徑長度
    for i in range(4): # 如果蛇頭和蛇尾緊挨著，則返回False。即不能follow_tail，追著蛇尾運動了
        if is_move_possible(tmpsnake[HEAD], mov[i]) and tmpsnake[HEAD]+mov[i]==tmpsnake[tmpsnake_size-1] and tmpsnake_size>3:
            result = False
    return result
 
# 讓蛇頭朝著蛇尾執行一步
# 不管蛇身阻擋，朝蛇尾方向執行
def follow_tail():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard) # 重置虛擬board
    tmpboard[tmpsnake[tmpsnake_size-1]] = FOOD # 讓蛇尾成為食物
    tmpboard[food] = SNAKE # 讓食物的地方變成蛇身
    board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # 求得各個位置到達蛇尾的路徑長度
    tmpboard[tmpsnake[tmpsnake_size-1]] = SNAKE # 還原蛇尾
 
    return choose_longest_safe_move(tmpsnake, tmpboard) # 返回執行方向(讓蛇頭運動1步)
 
# 在各種方案都不行時，隨便找一個可行的方向來走(1步),
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
    win.addch(int(food/WIDTH), food%WIDTH, '@')
 
# 真正的蛇在這個函式中，朝pbest_move走1步
def make_move(pbest_move):
    global key, snake, board, snake_size, score
    shift_array(snake, snake_size)
    snake[HEAD] += pbest_move
     
 
    # 按esc退出，getch同時保證繪圖的流暢性，沒有它只會看到最終結果
    win.timeout(10)
    event = win.getch()
    key = key if event == -1 else event
    if key == 27: return
 
    p = snake[HEAD]
    win.addch(int(p/WIDTH), p%WIDTH, '*')
 
     
    # 如果新加入的蛇頭就是食物的位置
    # 蛇長加1，產生新的食物，重置board(因為原來那些路徑長度已經用不上了)
    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE # 新的蛇頭
        snake_size += 1
        score += 1
        if snake_size < FIELD_SIZE: new_food()
    else: # 如果新加入的蛇頭不是食物的位置
        board[snake[HEAD]] = SNAKE # 新的蛇頭
        board[snake[snake_size]] = UNDEFINED # 蛇尾變為空格
        win.addch(int (snake[snake_size]/WIDTH), snake[snake_size]%WIDTH, ' ')
 
# 虛擬地執行一次，然後在呼叫處檢查這次執行可否可行
# 可行才真實執行。
# 虛擬執行吃到食物後，得到虛擬下蛇在board的位置
def virtual_shortest_move():
    global snake, board, snake_size, tmpsnake, tmpboard, tmpsnake_size, food
    tmpsnake_size = snake_size
    tmpsnake = snake[:] # 如果直接tmpsnake=snake，則兩者指向同一處記憶體
    tmpboard = board[:] # board中已經是各位置到達食物的路徑長度了，不用再計算
    board_reset(tmpsnake, tmpsnake_size, tmpboard)
     
    food_eated = False
    while not food_eated:
        board_refresh(food, tmpsnake, tmpboard)    
        move = choose_shortest_safe_move(tmpsnake, tmpboard)
        shift_array(tmpsnake, tmpsnake_size)
        tmpsnake[HEAD] += move # 在蛇頭前加入一個新的位置
        # 如果新加入的蛇頭的位置正好是食物的位置
        # 則長度加1，重置board，食物那個位置變為蛇的一部分(SNAKE)
        if tmpsnake[HEAD] == food:
            tmpsnake_size += 1
            board_reset(tmpsnake, tmpsnake_size, tmpboard) # 虛擬執行後，蛇在board的位置(label101010)
            tmpboard[food] = SNAKE
            food_eated = True
        else: # 如果蛇頭不是食物的位置，則新加入的位置為蛇頭，最後一個變為空格
            tmpboard[tmpsnake[HEAD]] = SNAKE
            tmpboard[tmpsnake[tmpsnake_size]] = UNDEFINED
 
# 如果蛇與食物間有路徑，則呼叫本函式
def find_safe_way():
    global snake, board
    safe_move = ERR
    # 虛擬地執行一次，因為已經確保蛇與食物間有路徑，所以執行有效
    # 執行後得到虛擬下蛇在board中的位置，即tmpboard，見label101010
    virtual_shortest_move() # 該函式唯一呼叫處
    if is_tail_inside(): # 如果虛擬執行後，蛇頭蛇尾間有通路，則選最短路執行(1步)
        return choose_shortest_safe_move(snake, board)
    safe_move = follow_tail() # 否則虛擬地follow_tail 1步，如果可以做到，返回true
    return safe_move
 
 
curses.initscr()
win = curses.newwin(HEIGHT, WIDTH, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)
win.addch(int(food/WIDTH), food%WIDTH, '@')
 
     
while key != 27:
    win.border(0)
    win.addstr(0, 2, 'S:' + str(score) + ' ')               
    win.timeout(10)
    # 接收鍵盤輸入，同時也使顯示流暢
    event = win.getch()
    key = key if event == -1 else event
    # 重置矩陣
    board_reset(snake, snake_size, board)
     
    # 如果蛇可以吃到食物，board_refresh返回true
    # 並且board中除了蛇身(=SNAKE)，其它的元素值表示從該點運動到食物的最短路徑長
    if board_refresh(food, snake, board):
        best_move  = find_safe_way() # find_safe_way的唯一呼叫處
    else:
        best_move = follow_tail()
             
    if best_move == ERR:
        best_move = any_possible_move()
    # 上面一次思考，只得出一個方向，執行一步
    if best_move != ERR: 
        make_move(best_move) 
    else: break       
         
curses.endwin()
print("\nScore - " + str(score))