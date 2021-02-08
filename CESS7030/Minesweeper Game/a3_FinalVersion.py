import random
import tkinter as tk
import sys
import csv
import os
import heapq
from tkinter import filedialog
from tkinter import messagebox
TASK_ONE=1
TASK_TWO=2
FLAG = "♥"
UNEXPOSED = "~"
POKEMON="☺"


class BoardModel(object):
    """The actual pokemon game with list format"""
    def __init__(self, grid_size, num_pokemon):
        """Construct a new pokemon game"""
        self._grid_size= grid_size
        self._num_pokemon= num_pokemon
        self._pokemon_locations=self.generate_pokemons()
        self._game = self.set_game()
        self._attempted_catches = self.get_attempted_catches()
        

    def set_game(self):
        """initialize the game string"""
        game_set=[]
        for n in range(0,self._grid_size**2):
            game_set.append(UNEXPOSED)
        return game_set
    def get_game(self):
        """return the game string"""
        return self._game
    
    def get_pokemon_locations(self):
        """return the pokemon_locations"""
        return self._pokemon_locations
    

    def get_attempted_catches(self):
        """calculate the number of flag in the game and use it as attempted_catches"""
        game = self._game
        k=0
        for g in game:
            if g == FLAG:
                k=k+1
        self._attempted_catches = k
        return self._attempted_catches
    
    def get_num_pokemon(self):
        """return the number of pokemon"""
        return self._num_pokemon
    def check_win(self):
        """check whether the player is win or not"""
        count=0
        for g in self._game:
            if g==FLAG:
                count=count+1
        if count==self._num_pokemon:
            for x in self._pokemon_locations:
                if self._game[x]!=FLAG:
                    return False
            for g in self._game:
                if g==UNEXPOSED:
                    return False
            return True
        else:
            return False
    def index_to_position(self,index):
        """change index into position"""
        col = index % self._grid_size
        row = index // self._grid_size
        return(col,row)
    def generate_pokemons(self):
        """generate pokemon locations"""
        cell_count = self._grid_size ** 2
        pokemon_locations = ()

        for _ in range(self._num_pokemon):
            if len(pokemon_locations) >= cell_count:
                break
            index = random.randint(0, cell_count-1)

            while index in pokemon_locations:
                index = random.randint(0, cell_count-1)

            pokemon_locations += (index,)

        return pokemon_locations


class PokemonGame():
    """The controller class of the game"""
    def __init__(self, master, grid_size=10, num_pokemon=15,task=TASK_ONE):
        """Bind the button and construct the View class and the Game class"""
        self._task= task
        self._master=master
        self._grid_size= grid_size
        self._num_pokemon= num_pokemon

        label = tk.Label(self._master, text="Pokemon: Got 2 Find Them All!", bg="pink", width=30, height=1, fg="white")
        label.pack(fill=tk.X,expand=0,side=tk.TOP)


        self._BM = BoardModel(self._grid_size, self._num_pokemon)
        self._BM._game = self._BM.get_game()
        self._BM._pokemon_locations = self._BM.get_pokemon_locations()
        self._BM._num_attempted_catches = self._BM.get_attempted_catches()


        self._master.geometry("{}x{}".format("600","600"))
        self._master.title("Pokemon: Got 2 Find Them All!")

        if self._task==TASK_TWO:
            self._BV = ImageBoardView(master,self._grid_size,self._BM)
            self._SB = StatusBar(self._master,self._BM,self._BV)
        else:
            self._BV = BoardView(master,self._grid_size)
        self._BV.draw_board(self._BM._game)
        self._BV.bind("<Button-1>", self.press_left)
        self._BV.bind("<Button-2>", self.press_left)
        self._BV.bind("<Button-3>", self.press_right)
        if self._task==TASK_TWO:
            self._BV.bind("<Motion>", self.Hover_TWO)
        else:
            self._BV.bind("<Motion>", self.Hover_ONE)
        self._index_shining = -1
        self._List_Image = [
            tk.PhotoImage(file="images/unrevealed.png"),
            tk.PhotoImage(file="images/unrevealed_moved.png"),
            ]
    def Hover_ONE(self, e):
        """When the model is in TASK_ONE the mouse hover on the canvas can make some animation"""
        x = e.x/self._BV._side_length
        y = e.y/self._BV._side_length
        index = self._BV.pixel_to_index((e.x,e.y))
        if x>=self._grid_size or y>=self._grid_size:
            pass
        else:
            index = self._BV.pixel_to_index((e.x,e.y))
            if self._BM._game[index]==UNEXPOSED and self._index_shining!= index:
                if self._index_shining >= 0:
                    pixel = self._BV.index_to_pixel(self._index_shining)
                    gb=self._BV.get_bbox(pixel)
                    self._BV.create_rectangle([gb], outline='black')
                pixel = self._BV.index_to_pixel(index)
                gb=self._BV.get_bbox(pixel)
                self._BV.create_rectangle([gb], outline='white')
                self._index_shining= index
            if self._BM._game[index]!=UNEXPOSED:
                pixel = self._BV.index_to_pixel(self._index_shining)
                gb=self._BV.get_bbox(pixel)
                self._BV.create_rectangle([gb], outline='black')
                self._index_shining= index
                
    def Hover_TWO(self, e):
        """When the model is in TASK_TWO the mouse hover on the canvas can make some animation"""
        x = e.x/self._BV._side_length
        y = e.y/self._BV._side_length
        index = self._BV.pixel_to_index((e.x,e.y))
        if x>=self._grid_size or y>=self._grid_size:
            pass
        else:
            index = self._BV.pixel_to_index((e.x,e.y))
            if self._BM._game[index]==UNEXPOSED and self._BM._game[self._index_shining]==UNEXPOSED:
                if self._index_shining >= 0:
                    pixel = self._BV.index_to_pixel(self._index_shining)
                    im = self._BV.create_image(pixel[0],pixel[1],image=self._List_Image[0])
                pixel = self._BV.index_to_pixel(index)
                im = self._BV.create_image(pixel[0],pixel[1],image=self._List_Image[1])
                self._index_shining= index
            elif self._BM._game[index]==UNEXPOSED and self._BM._game[self._index_shining]!=UNEXPOSED:
                pixel = self._BV.index_to_pixel(index)
                im = self._BV.create_image(pixel[0],pixel[1],image=self._List_Image[1])
                self._index_shining= index
            elif self._BM._game[index]!=UNEXPOSED and self._BM._game[self._index_shining]==UNEXPOSED:
                pixel = self._BV.index_to_pixel(self._index_shining)
                im = self._BV.create_image(pixel[0],pixel[1],image=self._List_Image[0])
                self._index_shining= index
            else:
                self._index_shining= index
            
    def press_left(self, e):
        '''click event for left click'''
        x = e.x/self._BV._side_length
        y = e.y/self._BV._side_length
        if x>self._grid_size or y>self._grid_size:
            pass
        else:
            index = self._BV.pixel_to_index((e.x,e.y))
            if self._BM._game[index]==UNEXPOSED and index not in self._BM._pokemon_locations:
                x=self.number_at_cell(self._BM._game, self._BM._pokemon_locations, self._grid_size, index)
                self._BM._game[index]=x
                big_search=self.big_fun_search(self._BM._game, self._grid_size, self._BM._pokemon_locations, index)
                for bfs in big_search:
                    number_at_cell=self.number_at_cell(self._BM._game, self._BM._pokemon_locations, self._grid_size, bfs)
                    if self._BM._game[bfs]!=FLAG:
                        self._BM._game[bfs]=number_at_cell
                self._BV.draw_board(self._BM._game)
                if self._BM.check_win()==True:
                    if self._task==TASK_TWO:
                        self._SB._isLoss=True
                        self._BV.win_Records(self._SB.change_time(self._SB._time)[0],self._SB.change_time(self._SB._time)[1])
                    else:
                        self._BV.win()
                    #self._master.destroy()
            elif self._BM._game[index]==FLAG:
                self._BM._game[index]=UNEXPOSED
                if self._task==TASK_TWO:
                    self._SB.update_attempted_catches(self._BM)
                self._BV.draw_board(self._BM._game)
            elif index in self._BM._pokemon_locations and self._BM._game[index]==UNEXPOSED:
                for n in self._BM._pokemon_locations:
                    self._BM._game[n]=POKEMON
                self._BV.draw_board(self._BM._game)
                if self._task==TASK_TWO:
                    self._SB._isLoss=True
                    self._BV.quit()
                else:
                    self._BV.quit()
            else:
                pass


    def press_right(self, e):
        '''click event for right click'''
        x = e.x/self._BV._side_length
        y = e.y/self._BV._side_length
        if x>self._grid_size or y>self._grid_size:
            pass
        else:
            index = self._BV.pixel_to_index((e.x,e.y))
            if self._BM._game[index]==UNEXPOSED:
                self._BM._game[index]=FLAG
                if self._task==TASK_TWO:
                    self._SB.update_attempted_catches(self._BM)
                if self._BM.check_win()==True:
                    self._BM._game[index]=FLAG
                    self._BV.draw_board(self._BM._game)
                    if self._task==TASK_TWO:
                        self._SB._isLoss=True
                        self._BV.win_Records(self._SB.change_time(self._SB._time)[0],self._SB.change_time(self._SB._time)[1])
                    else:
                        self._BV.win()
                else:
                    self._BV.draw_board(self._BM._game)
                    

    def neighbour_directions(self,index, grid_size):
        '''find the neighbour of one specific cell'''
        neighbour_perfact = [(index-grid_size)-1, index-grid_size, (index-grid_size)+1, index-1, index+1, (index+grid_size)-1, index+grid_size, (index+grid_size)+1]
        neighbour=[]
        gz = grid_size*grid_size-1
        tp1 = (index//grid_size,index%grid_size)
        for n in neighbour_perfact:
            tp = (n//grid_size,n%grid_size)
            if n > gz or n < 0:
                continue
            if (tp[0]-tp1[0])**2+(tp[1]-tp1[1])**2>2 :
                continue
            neighbour.append(n)
        return neighbour

    def number_at_cell(self,game, pokemon_locations, grid_size, index):
        '''find out how much pokemon adjacent to the grid'''
        number = 0
        for neighbour in self.neighbour_directions(index, grid_size):
            if neighbour in pokemon_locations:
                number += 1
        return number

    def big_fun_search(self,game, grid_size, pokemon_locations, index):
        '''use recursion to reveal the grid'''
        queue = [index]
        discovered = [index]
        visible = []
    
        if game[index] == FLAG:
            return queue
    
        number = self.number_at_cell(game, pokemon_locations, grid_size, index)
        if number != 0:
            return queue
    
        while queue:
            node = queue.pop()
            for neighbour in self.neighbour_directions(node, grid_size):
                if neighbour in discovered:
                    continue
    
                discovered.append(neighbour)
                if game[neighbour] != FLAG:
                    number = self.number_at_cell(game, pokemon_locations, grid_size, neighbour)
                    if number == 0:
                        queue.append(neighbour)
                visible.append(neighbour)
        return visible




class BoardView(tk.Canvas):
    '''use canvas to do the viewing'''
    def __init__(self, master,grid_size,board_width=600,*args,**kwargs):
        '''inherit from the Tk.Canvas and draw the view of the game'''
        super().__init__(master,width=board_width,height=board_width)
        self._grid_size= grid_size
        self._board_width=board_width
        self._side_length = int((self._board_width/self._grid_size)*0.9)
        self._side_half_length = int(self._side_length/2)
        self._side_whole_length = self._side_length*self._grid_size

        
    def draw_board(self,board):
        '''draw the game on canvas'''
        self.delete("all")
        self.pack(fill=tk.BOTH, expand=1,side=tk.TOP)
        for x in range(self._side_length,self._side_whole_length,self._side_length):
            self.create_line(x, 0, x, self._side_whole_length, fill="black")
        for y in range(self._side_length,self._side_whole_length,self._side_length):
            self.create_line(0, y, self._side_whole_length, y, fill="black")
        for b in range(len(board)):
            if board[b] == UNEXPOSED:
                pixel = self.index_to_pixel(b)
                gb=self.get_bbox(pixel)
                self.create_rectangle([gb], fill="forestgreen")
            elif board[b] == FLAG:
                pixel = self.index_to_pixel(b)
                gb=self.get_bbox(pixel)
                self.create_rectangle([gb], fill="red")
            elif board[b] == POKEMON:
                pixel = self.index_to_pixel(b)
                gb=self.get_bbox(pixel)
                self.create_rectangle([gb], fill="yellow")
            else:
                k=board[b]
                pixel = self.index_to_pixel(b)
                gb=self.get_bbox(pixel)
                self.create_rectangle([gb], fill="palegreen")
                pixel = self.index_to_pixel(b)
                self.create_text(pixel[0],pixel[1],fill="black",text=k)
        
    def get_bbox(self, pixel):
        '''use the pixel to output the grid's North-West point and South-East point'''
        x1=pixel[0]
        y1=pixel[1]
        x=x1//self._side_length
        y=y1//self._side_length
        x2=x*self._side_length
        y2=y*self._side_length
        return (x2,y2,x2+self._side_length,y2+self._side_length)
    def position_to_pixel(self, position):
        '''changge the position to pixel'''
        x=position[0]*self._side_length+self._side_half_length
        y=position[1]*self._side_length+self._side_half_length
        return (x,y)

    def index_to_pixel(self, index):
        ''' transfer the index to pixel'''
        position=(index%self._grid_size,index//self._grid_size)
        x=position[0]*self._side_length+self._side_half_length
        y=position[1]*self._side_length+self._side_half_length
        return (x,y)
    def pixel_to_position(self, pixel):
        '''transfer the pixel to position'''
        x=pixel[0]//self._side_length
        y=pixel[1]//self._side_length
        return(x,y)
    def pixel_to_index(self, pixel):
        '''change the index to pixel'''
        x=pixel[0]//self._side_length
        y=pixel[1]//self._side_length
        index= x+y*self._grid_size
        return int(index)

    def quit(self):
        '''quit the game and destroy the master'''
        ans = messagebox.showinfo("Game Over","You scared away the pokemon")
        if ans:
            self.master.destroy()

    def win(self):
        '''when the player win the game it would come out'''
        ans = messagebox.showinfo("Congragulations","You have catched all the pokemon")
        if ans:
            self.master.destroy()


class StatusBar(tk.Frame):
    '''StatusBar displays other game's information'''
    def __init__(self, master,*args,**kwargs):
        '''Construct a tk.Frame at the bottom side of the game'''
        super().__init__(master)
        self._GM = args[0]
        self._GV = args[1]
        self._time = 0
        self._filename = ""
        self._master = master
        self._isLoss = False
        self._List_Image = [
            tk.PhotoImage(file="images/pokeball.png"),
            tk.PhotoImage(file="images/empty_pokeball.png"),
            tk.PhotoImage(file="images/full_pokeball.png"),
            tk.PhotoImage(file="images/clock.png"),
            ]
        
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save Game", command=self.Save_Records)
        filemenu.add_command(label="Load Game", command=self.Load_Records)
        filemenu.add_command(label="Restart Game", command=self.Restart_Game)
        filemenu.add_command(label="New Game", command=self.New_Game)
        filemenu.add_command(label="Quit", command=self.Quit_Game)
        filemenu.add_command(label="High_Scores", command=self.Display_Records)

        
        self._Bottom_Controls = tk.Frame(self._master, bg='white', height=59)
        self._label_Wall = tk.Label(self._Bottom_Controls, bg='white', width=9)
        self._label_Wall.pack(side=tk.LEFT)
        
        self._label_PokemonBall = tk.Label(self._Bottom_Controls, image=self._List_Image[2])
        self._label_PokemonBall.pack(side=tk.LEFT)
        self._label_Attempt_Text = tk.Frame(self._Bottom_Controls, bg='white')
        self._label_Attempt_Text_UP = tk.Label(self._label_Attempt_Text, bg='white',text="      {} attemped catches".format(self._GM.get_attempted_catches()))
        self._label_Attempt_Text_UP.pack(side=tk.TOP)
        self._label_Attempt_Text_DOWN = tk.Label(self._label_Attempt_Text, bg='white',text="{} pokeballs left".format(self._GM._num_pokemon - self._GM.get_attempted_catches()))
        self._label_Attempt_Text_DOWN.pack(side=tk.BOTTOM)
        self._label_Attempt_Text.pack(side=tk.LEFT)



        self._label_Wall = tk.Label(self._Bottom_Controls, bg='white', width=3)
        self._label_Wall.pack(side=tk.LEFT)

        self._label_Clock = tk.Label(self._Bottom_Controls, image=self._List_Image[3])
        self._label_Clock.pack(side=tk.LEFT)
        self._label_Clock_Text = tk.Frame(self._Bottom_Controls, bg='white')
        self._label_Clock_UP = tk.Label(self._label_Clock_Text, bg='white',text="Time elapsed")
        self._label_Clock_UP.pack(side=tk.TOP)
        self._label_Clock_DOWN = tk.Label(self._label_Clock_Text, bg='white',text="{}m {}s".format(self.change_time(self._time)[0],self.change_time(self._time)[1]))
        self._label_Clock_DOWN.pack(side=tk.BOTTOM)
        self._label_Clock_Text.pack(side=tk.LEFT)


        self._label_Wall = tk.Label(self._Bottom_Controls, bg='white', width=3)
        self._label_Wall.pack(side=tk.LEFT)



        self._Button_Frame = tk.Frame(self._Bottom_Controls, bg='white')
        self._Button_Top = tk.Button(self._Button_Frame, text="New Game", bg="white" ,command=self.New_Game)
        self._Button_Top.pack(side=tk.TOP)
        self._Button_Bottom = tk.Button(self._Button_Frame, text="Restart Game", bg="white",command=self.Restart_Game)
        self._Button_Bottom.pack(side=tk.BOTTOM)
        self._Button_Frame.pack(side=tk.LEFT)
        
        self._Bottom_Controls.pack(side=tk.BOTTOM,fill=tk.BOTH)

        self.update_time()

    def Quit_Game(self):
        '''quit the game'''
        self._master.destroy()
    def Save_Records(self):
        ''' save the record'''
        filename = filedialog.asksaveasfilename(initialfile='Untitled.csv',defaultextension=".csv",filetypes=[("CSV files","*.csv")])
        if filename :
            self._filename = filename
        self.perform_save()
        
    def Load_Records(self):
        ''' load the game from the records'''
        self._filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes=[("CSV files","*.csv")])
        if self._filename :
            f = open(self._filename, "r")
            text = f.read()
        text = text.split("\n")
        self._GM._game = eval(text[0])
        self._GM._pokemon_locations = eval(text[1])
        self._GV.draw_board(self._GM._game)
        self._time = int(text[2])


    def perform_save(self):
        '''save the game, pokemonlocation and time'''
        if self._filename:
            self._master.title("Text Editor: {0}".format(self._filename))
            f = open(self._filename, "w")
            X=self._GM.get_game()
            Y=self._GM.get_pokemon_locations()
            Z=self._time
            text=str(X)+"\n"+str(Y)+"\n"+str(Z)
            f.write(text)
            f.close()
    def New_Game(self):
        '''construct a new game'''
        self._master.destroy()
        main()
    def Restart_Game(self):
        '''restart the game'''
        self._time=0
        self._GM._game = self._GM.set_game()
        self._GV.draw_board(self._GM._game)
    def update_attempted_catches(self, GM):
        ''' when a click event happened update the attempt catches '''
        GM_ac = GM.get_attempted_catches()
        self._label_Attempt_Text_UP.config(text="      {} attemped catches".format(GM_ac) )
        
        GM_np_ac = GM._num_pokemon - GM.get_attempted_catches()
        if GM_np_ac > 0:
            self._label_Attempt_Text_DOWN.config(text="{} pokeballs left".format(GM_np_ac))
            self._label_PokemonBall.config(image=self._List_Image[2])
        elif GM_np_ac==0:
            self._label_Attempt_Text_DOWN.config(text="{} pokeballs left".format(GM_np_ac))
            self._label_PokemonBall.config(image=self._List_Image[1])
        else:
            self._label_Attempt_Text_DOWN.config(text="{} pokeballs left".format(0)) 
    def update_time(self):
        ''' update the time every second'''
        if self._isLoss == False :
            self._time = self._time+1
            self._label_Clock_DOWN.config(text="{}m {}s".format(self.change_time(self._time)[0],self.change_time(self._time)[1]))
            self._Button_Frame.after(1000,self.update_time)
        else:
            pass

    def change_time(self,seconds):
        ''' transfer the total seconds into the format of m and s'''
        timer_minute = seconds//60
        timer_seconds = seconds - 60*timer_minute
        return (timer_minute,timer_seconds)
    
    def Display_Records(self):
        ''' read the records file and choose the top three fast records'''
        self._Victory = {}
        path = "Record.csv"
        root = tk.Tk()
        root.title('Top 3')
        label = tk.Label(root, text='High Score',font=('microsoft yahei', 16, 'bold'),bg="pink", fg="white")
        label.pack(side=tk.TOP)

        if os.path.exists(path) == True:
            with open(path,"r") as f:
                k=[]
                csv_read = csv.reader(f)
                for line in csv_read:
                    if len(line)>=1:
                        self._Victory[int(line[2])]=line[0]

                f.close()
                Top = heapq.nsmallest(3, self._Victory)
                for t in Top:
                    label = tk.Label(root, text=self._Victory[t]+":"+str(t)+"s", bg="white", fg="black")
                    label.pack(side=tk.TOP, fill=tk.X,expand=0)
        else:
            label = tk.Label(root, text="Have not winner yet.", bg="white", fg="black")
            label.pack(side=tk.TOP, fill=tk.X,expand=0)
                
        calc = tk.Button(root, text="Done", command=lambda:self.End_Display(root), bg="white", fg="black")
        calc.pack(side=tk.TOP, fill=tk.X,expand=1)


    def End_Display(self,root):
        ''' destroy the tk'''
        root.destroy()

class ImageBoardView(BoardView):
    ''' the BosrdView for TASK_TWO'''
    def __init__(self, master,grid_size,board_width=600,*args,**kwargs):
        ''' Different from TASK_ONE the ImageBoardView use image rather than canvas'''
        super().__init__(master,grid_size,board_width=600,*args,**kwargs)
        self._side_length = int(self._board_width/self._grid_size)
        self._side_half_length = int((self._board_width/self._grid_size)/2)
        self._List_Image = [
            tk.PhotoImage(file="images/zero_adjacent.png"),
            tk.PhotoImage(file="images/one_adjacent.png"),
            tk.PhotoImage(file="images/two_adjacent.png"),
            tk.PhotoImage(file="images/three_adjacent.png"),
            tk.PhotoImage(file="images/four_adjacent.png"),
            tk.PhotoImage(file="images/five_adjacent.png"),
            tk.PhotoImage(file="images/six_adjacent.png"),
            tk.PhotoImage(file="images/seven_adjacent.png"),
            tk.PhotoImage(file="images/eight_adjacent.png"),
            tk.PhotoImage(file="images/unrevealed.png"),
            tk.PhotoImage(file="images/pokeball.png"),
            tk.PhotoImage(file="images/empty_pokeball.png"),
            tk.PhotoImage(file="images/full_pokeball.png"),
            tk.PhotoImage(file="images/clock.png")
            ]
        self._List_PokemonImage = [
            tk.PhotoImage(file="images/pokemon_sprites/charizard.png"),
            tk.PhotoImage(file="images/pokemon_sprites/cyndaquil.png"),
            tk.PhotoImage(file="images/pokemon_sprites/pikachu.png"),
            tk.PhotoImage(file="images/pokemon_sprites/psyduck.png"),
            tk.PhotoImage(file="images/pokemon_sprites/togepi.png"),
            tk.PhotoImage(file="images/pokemon_sprites/umbreon.png")
            ]
    def draw_board(self,board):
        '''draw the game board'''
        self.delete("all")
        self.pack(fill=tk.BOTH, expand=1)
        for x in range(self._side_length,self._board_width,self._side_length):
            self.create_line(x, 0, x, self._board_width, fill="black")
        for y in range(self._side_length,self._board_width,self._side_length):
            self.create_line(0, y, self._board_width, y, fill="black")
        for b in range(len(board)):
            if board[b] == UNEXPOSED:
                pixel = self.index_to_pixel(b)
                im = self.create_image(pixel[0],pixel[1],image=self._List_Image[9])
            elif board[b] == FLAG:
                pixel = self.index_to_pixel(b)
                im = self.create_image(pixel[0],pixel[1],image=self._List_Image[10])
            elif board[b] == POKEMON:
                pixel = self.index_to_pixel(b)
                ran = random.randint(0,5)
                im = self.create_image(pixel[0],pixel[1],image=self._List_PokemonImage[ran])
            else:
             x=board[b]
             pixel = self.index_to_pixel(b)
             im = self.create_image(pixel[0],pixel[1],image=self._List_Image[x])
             
    def quit(self):
        '''quit the game if the player click no, restart the game if the player click yes'''
        ans = messagebox.askquestion("Game Over","You lose! Would you like to play again?")
        if ans=="yes":
            self.master.destroy()
            main()
        else:
            self.master.destroy()

    def win(self):
        ''' quit the game when the player win'''
        ans = messagebox.showinfo("Congragulations","You have catched all the pokemon")
        if ans:
            self.master.destroy()
            
    def Enter_Record(self,time,root):
        ''' save the record'''
        name = self.entry.get()
        content = [name,":",time]
        path = "Record.csv"
        if os.path.exists(path) == False:
            with open(path,"a", newline='') as f:
                csv_write = csv.writer(f)
                csv_write.writerow(content)
                f.close()
                root.destroy()
                self.master.destroy()
        else:
            with open(path,"a", newline='') as f:
                csv_write = csv.writer(f)
                csv_write.writerow(content)
                f.close()
                root.destroy()
                self.master.destroy()
        
    def win_Records(self,m,s):
        ''' if the player win they can save their record'''
        time=60*m+s
        root = tk.Tk()
        root.title('You win!')
        label = tk.Label(root, text='You won in {}m and {}s! Enter your name:'.format(m,s))
        label.pack(side=tk.TOP)
        self.entry = tk.Entry(root, width=20)
        self.entry.pack(side=tk.TOP)
        calc = tk.Button(root, text="Enter", command=lambda:self.Enter_Record(time,root))
        calc.pack(side=tk.TOP)
        root.mainloop()


            
        
        
def main():
    """
    Handles player interaction.
    """
    root = tk.Tk()
    PG = PokemonGame(root,10,12,TASK_TWO)
    root.update()
    root.mainloop()
    

if __name__ == '__main__' :
    main()
    
