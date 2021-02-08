EMPTY_TILE = "tile"
START_PIPE = "start"
END_PIPE = "end"
LOCKED_TILE = "locked"

SPECIAL_TILES = {
    "S": START_PIPE,
    "E": END_PIPE,
    "L": LOCKED_TILE
}

PIPES = {
    "ST": "straight",
    "CO": "corner",
    "CR": "cross",
    "JT": "junction-t",
    "DI": "diagonals",
    "OU": "over-under"
}

### add code here ###
class Tile(object):
    '''
萨达撒多
    '''
    def __init__(self, name, selectable=True):
        '''我是一条注释'''
        self._name = name
        self._id = 'tile'
        self._select = selectable
    def get_name(self):
        '''我是一条注释'''
        return self._name
    def get_id(self):
        '''我是一条注释'''
        return self._id
    def set_select(self, selectable=True):
        '''我是一条注释'''
        self._select = selectable
    def can_select(self):
        '''我是一条注释'''
        if self._select == True:
            return True
        else:
            return False
    def __str__(self):
        '''我是一条注释'''
        return 'Tile(\'{0}\', {1})'.format(self._name,self._select)
    def __repr__(self):
        '''我是一条注释'''
        return 'Tile(\'{0}\', {1})'.format(self._name,self._select)
    
class Pipe(Tile):
    '''我是一条注释'''
    def __init__(self, name, orientation=0, selectable=True):
        '''我是一条注释'''
        self._name = name
        self._orientation = orientation
        self._select = selectable
        self._id = 'pipe'
    def get_connected(self,side):#不懂
        '''我是一条注释'''
        if self._name == PIPES['ST']:
            sidelist=[]
            if self._orientation==0 or self._orientation==2:
                sidelist.append('N')
                sidelist.append('S')
            if self._orientation==1 or self._orientation==3:
                sidelist.append('W')
                sidelist.append('E')
            if side in sidelist:
                sidelist.remove(side)
                return sidelist
            else:
                sidelist=[]
                return sidelist
        if self._name == PIPES['CO']:
            sidelist=[]
            if self._orientation==0:
                sidelist.append('N')
                sidelist.append('E')
            if self._orientation==1:
                sidelist.append('E')
                sidelist.append('S')
            if self._orientation==2:
                sidelist.append('S')
                sidelist.append('W')
            if self._orientation==3:
                sidelist.append('N')
                sidelist.append('W')
            if side in sidelist:
                sidelist.remove(side)
                return sidelist
            else:
                sidelist=[]
                return sidelist
        if self._name == PIPES['CR']:
            sidelist=[]
            sidelist.append('N')
            sidelist.append('W')
            sidelist.append('S')
            sidelist.append('E')
            if side in sidelist:
                sidelist.remove(side)
                return sidelist
            else:
                sidelist=[]
                return sidelist
        if self._name == PIPES['JT']:
            sidelist=[]
            if self._orientation==0:
                sidelist.append('S')
                sidelist.append('W')
                sidelist.append('E')
            if self._orientation==1:
                sidelist.append('N')
                sidelist.append('W')
                sidelist.append('S')
            if self._orientation==2:
                sidelist.append('N')
                sidelist.append('W')
                sidelist.append('E')
            if self._orientation==3:
                sidelist.append('N')
                sidelist.append('E')
                sidelist.append('S')
            if side in sidelist:
                sidelist.remove(side)
                return sidelist
            else:
                sidelist=[]
                return sidelist
        if self._name == PIPES['DI']:
            sidelist1=[]
            sidelist2=[]
            if self._orientation==0 or self._orientation==2:
                sidelist1.append('N')
                sidelist1.append('E')
                sidelist2.append('W')
                sidelist2.append('S')
            if self._orientation==1 or self._orientation==3:
                sidelist1.append('N')
                sidelist1.append('W')
                sidelist2.append('S')
                sidelist2.append('E')
            if side in sidelist1:
                sidelist1.remove(side)
                return sidelist1
            if side in sidelist2:
                sidelist2.remove(side)
                return sidelist2
        if self._name == PIPES['OU']:
            sidelist1=[]
            sidelist2=[]
            sidelist1.append('W')
            sidelist1.append('E')
            sidelist2.append('N')
            sidelist2.append('S')
            if side in sidelist1:
                sidelist1.remove(side)
                return sidelist1
            if side in sidelist2:
                sidelist2.remove(side)
                return sidelist2
    def rotate(self,direction):#有问题
        '''我是一条注释'''
        if direction>0 and self._orientation<3 :
            self._orientation +=1
        elif self._orientation==3 :
            self._orientation=0
        elif direction<0 and self._orientation>0:
            self._orientation -=1
        else:
            self._orientation=3
    def get_orientation(self):
        '''我是一条注释'''
        return self._orientation
    def __str__(self):
        '''我是一条注释'''
        return 'Pipe(\'{0}\', {1})'.format(self._name,self._orientation)
    def __repr__(self):
        '''我是一条注释'''
        return 'Pipe(\'{0}\', {1})'.format(self._name,self._orientation)
    
class SpecialPipe(Pipe):
    '''
萨达撒多
    '''
    def __init__(self, name, orientation=0, selectable=False):
        '''我是一条注释'''
        self._name = name
        self._orientation = orientation
        self._select = selectable
        self._id = 'special_pipe'
        self._d = 3
    def __str__(self):
        '''我是一条注释'''
        if self._d == 0:
            name='StartPipe'
        elif self._d == 1:
            name='EndPipe'
        else:
            name='SpecialPipe'
        return "{0}({1})".format(name,self._orientation)
    def __repr__(self):
        '''我是一条注释'''
        if self._d == 0:
            name='StartPipe'
        elif self._d == 1:
            name='EndPipe'
        else:
            name='SpecialPipe'
        return "{0}({1})".format(name,self._orientation)
    
class StartPipe(SpecialPipe):
    '''
萨达撒多
    '''
    def __init__(self, orientation=0, selectable=False):
        '''我是一条注释'''
        #self._name = 'StartPipe'
        self._name = 'start'
        self._orientation = orientation
        self._select = selectable
        self._id = 'special_pipe'
        self._d = 0
    def get_connected(self,side=None):
        '''我是一条注释'''
        if self._orientation==0:
            return ['N']
        if self._orientation==1:
            return ['E']
        if self._orientation==2:
            return ['S']
        if self._orientation==3:
            return ['W']
        
class EndPipe(SpecialPipe):
    '''我是一条注释'''
    def __init__(self, orientation=0, selectable=False):
        '''我是一条注释'''
        #self._name = 'EndPipe'
        self._name = 'end'
        self._orientation = orientation
        self._select = selectable
        self._id = 'special_pipe'
        self._d = 1
    def get_connected(self,side=None):
        '''我是一条注释'''
        if self._orientation==0:
            return ['S']
        if self._orientation==1:
            return ['W']
        if self._orientation==2:
            return ['N']
        if self._orientation==3:
            return ['E']

def partition_list(ls, size):
    """
    Returns a new list with elements
    of which is a list of certain size.

        >>> partition([1, 2, 3, 4], 3)
        [[1, 2, 3], [4]]
    """
    return [ls[i:i+size] for i in range(0, len(ls), size)]

class PipeGame:
    """
    A game of Pipes.
    """
    def __init__(self, game_file='game_1.csv'):
        """
        Construct a game of Pipes from a file name.

        Parameters:
            game_file (str): name of the game file.
        """
        def fine_fine(filename):
            line_number_number=0
            with open(filename) as fin:
                for line in fin:
                    line_number_number+=1
                fin.close()
            line_number_number = line_number_number - 1
            return line_number_number
        def fine_functions(filename):
            line_number=0
            with open(filename) as fin:
                for line in fin:
                    line_number+=1
                fin.close()

            with open(filename) as fin:
                count=0
                for line in fin:
                    count+=1
                    while count>= line_number:
                        line = line.split(',')
                        playable_pipes = {'straight': int(line[0]), 'corner': int(line[1]), 'cross': int(line[2]), 'junction-t': int(line[3]), 'diagonals': int(line[4]), 'over-under': int(line[5])}
                        break
                fin.close()

            with open(filename) as fin:
                count=0
                board_layout=[]
                for line in fin:
                    count+=1
                    if count>= line_number:
                        break
                    else:
                        line,_,_ = line.partition('\n')
                        line = line.split(',')

                        for l in line:
                            if l=='#' :
                                board_layout.append(Tile('tile', True))
                            elif l[0]=='S':
                                if len(l)==1:
                                    board_layout.append(StartPipe(1))
                                else:
                                    x = int(l[1])
                                    board_layout.append(StartPipe(x))
                            elif l[0]=='E':
                                if len(l)==1:
                                    board_layout.append(EndPipe(3))
                                else:
                                    x = int(l[1])
                                    board_layout.append(EndPipe(x))
                            elif l=='L' :
                                board_layout.append(Tile('locked', False))
                            else:
                                if len(l)>2:
                                    x = int(l[2])
                                else:
                                    x = 0
                                name = l[:2]
                                board_layout.append(Pipe(PIPES[name], x, False))
                board_layout = partition_list(board_layout, line_number-1)
                fin.close()
            return (playable_pipes,board_layout)

        game_combation = fine_functions(game_file)
        playable_pipes=game_combation[0]
        board_layout=game_combation[1]

        
        '''
        board_layout = [[Tile('tile', True), Tile('tile', True), Tile('tile', True), Tile('tile', True), \
        Tile('tile', True), Tile('tile', True)], [StartPipe(1), Tile('tile', True), Tile('tile', True), \
        Tile('tile', True), Tile('tile', True), Tile('tile', True)], [Tile('tile', True), Tile('tile', True), \
        Tile('tile', True), Pipe('junction-t', 0, False), Tile('tile', True), Tile('tile', True)], [Tile('tile', True), \
        Tile('tile', True), Tile('tile', True), Tile('tile', True), Tile('locked', False), Tile('tile', True)], \
        [Tile('tile', True), Tile('tile', True), Tile('tile', True), Tile('tile', True), EndPipe(3), \
        Tile('tile', True)], [Tile('tile', True), Tile('tile', True), Tile('tile', True), Tile('tile', True), \
        Tile('tile', True), Tile('tile', True)]]
        playable_pipes = {'straight': 1, 'corner': 1, 'cross': 1, 'junction-t': 1, 'diagonals': 1, 'over-under': 1}
        '''
        
        self._board_layout=board_layout
        self._playable_pipes=playable_pipes
        self._starting_position = ()
        self._ending_position = ()

        
        line_number_number = fine_fine(game_file)
        self._line_number = line_number_number
        ### add code here ###
    def get_board_layout(self):
        '''我是一条注释'''
        return self._board_layout
    def get_playable_pipes(self):
        '''我是一条注释'''
        return self._playable_pipes
    def change_playable_amount(self, pipe_name, number):
        '''我是一条注释'''
        self._playable_pipes[pipe_name]+=number
    def get_pipe(self,position):
        '''我是一条注释'''
        x=position[0]
        y=position[1]
        return self._board_layout[x][y]
    def set_pipe(self,pipe, position):
        '''我是一条注释'''
        x=position[0]
        y=position[1]
        self._board_layout[x][y]=pipe
        name=pipe._name
        self.change_playable_amount(name, -1)
    def pipe_in_position(self,position):
        '''我是一条注释'''
        if position==None :
            return None
        x=position[0]
        y=position[1]
        pipeId = self._board_layout[x][y]._id
        if pipeId == 'pipe'or pipeId == 'special_pipe' :
            return self._board_layout[x][y]
        else:
            return None
    def remove_pipe(self, position):
        '''我是一条注释'''
        x=position[0]
        y=position[1]
        name=self._board_layout[x][y]._name
        self._playable_pipes[name]+=1
        self._board_layout[x][y] = Tile('tile', True)
    def position_in_direction(self, direction, position):
        '''我是一条注释'''
        x=position[0]
        y=position[1]
        if direction=='N':
            direction='S'
            x=x-1
        elif direction=='S':
            direction='N'
            x+=1
        elif direction=='W':
            direction='E'
            y=y-1
        else:
            direction='W'
            y+=1
        if x<0:
            return None
        elif x>self._line_number-1:
            return None
        elif y<0:
            return None
        elif y>self._line_number-1:
            return None
        else:
            return (direction,(x,y))
    def end_pipe_positions(self):
        '''我是一条注释'''
        '''
        self._board_layout[1][0]=StartPipe(1)
        self._board_layout[4][4]=EndPipe(3)
        '''
        counti=0
        for i in self._board_layout :
            countj=0
            for j in i:
                if j.get_name()=='start':
                    self._starting_position = (counti,countj)
                elif j.get_name()=='end':
                    self._ending_position = (counti,countj)
                else:
                    countj+=1
            counti+=1
    def get_starting_position(self):
        '''我是一条注释'''
        self.end_pipe_positions()
        return self._starting_position
    def get_ending_position(self):
        '''我是一条注释'''
        self.end_pipe_positions()
        return self._ending_position

    def check_win(self):
        '''我是一条注释'''
        position = self.get_starting_position()
        pipe = self.pipe_in_position(position)
        queue = [(pipe, None, position)]
        discovered = [(pipe, None)]
        while queue:
            pipe, direction, position = queue.pop()
            for direction in pipe.get_connected(direction):
                if self.position_in_direction(direction, position) is None:
                    new_direction = None
                    new_position = None
                else:
                    new_direction, new_position = self.position_in_direction(direction, position)
                if new_position == self.get_ending_position() and direction == self.pipe_in_position(new_position).get_connected()[0]:
                    return True

                pipe = self.pipe_in_position(new_position)
                if pipe is None or (pipe, new_direction) in discovered:
                    continue
                discovered.append((pipe, new_direction))
                queue.append((pipe, new_direction, new_position))
        return False


def main():
    print("Please run gui.py instead")


if __name__ == "__main__":
    main()
