from a1_support import *

def display(grid_size):
    '''This def estabilished the initial game

    Parameters:
        grid_size (int): The grid size of the game.

    Returns:
        game (string): a string represents the clls in the game
    '''
    game=""
    for i in range(grid_size*grid_size):
        game=game+UNEXPOSED
    return game
def display_game(game,grid_size):
    '''out put the current game structure

    Parameters:
        grid_size (int): The grid size of the game.
        game (string): a string represents the clls in the game.

    Returns:
        game (string): a string represents the clls in the game.
    '''
    zero_line="----"
    for i in range(grid_size):
        zero_line+="----"

    first_line = "  |"
    for i in range(1,grid_size+1):
        if i<10 :
            first_line+=" {0} |".format(i)
        else:
            first_line+=" {0}|".format(i)
    print(first_line)
    print(zero_line)

    for i in range(grid_size):
        second_line = ""
        for j in range(grid_size):
            if j==0:
                second_line+="{0} |".format(ALPHA[i])
                second_line+=" {0} |".format(game[i*grid_size+j])
            else:
                second_line+=" {0} |".format(game[i*grid_size+j])
        print(second_line)
        print(zero_line)
                    
def parse_position(action, grid_size):
    '''out put the location of action refer to'''
    ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if len(action)<2:
        return None
    elif action[0] in ALPHA and action[1] in "0123456789" and int(action[1:])<= grid_size:
        for i in range(len(ALPHA)):
            while ALPHA[i]==action[0]:
                return(i,int(action[1:])-1)
    else:
        return None
def position_to_index(position, grid_size):
    '''return index'''
    return grid_size*position[0]+position[1]
def replace_character_at_index(game,index,character):
    '''uodate the game structure'''
    game=game[:index]+str(character)+game[index+1:]
    return game
def flag_cell(game,index):
    '''set flag'''
    if game[index]!=FLAG:
        game = replace_character_at_index(game,index,FLAG)
    else :
        game = replace_character_at_index(game,index,UNEXPOSED)
    return game
def index_in_direction(index, grid_size, direction):
    '''input index which with a direction'''
    intex=0
    if "up" in direction:
        intex=intex-grid_size
    if "down" in direction:
        intex=intex+grid_size
    if "right" in direction:
        intex=intex+1
    if "left" in direction:
        intex=intex-1
    neighbour = neighbour_directions(index, grid_size)
    if index+intex in neighbour:
        intex=index+intex
        index=intex
        return index
    else:
        return None
        
        
def neighbour_directions(index, grid_size):
    '''searching out these feasible neighbour'''
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
def number_at_cell(game, pokemon_locations, grid_size, index):
    '''the number of pokemons around the current cell'''
    neighbour = neighbour_directions(index, grid_size)
    count = 0
    for n in neighbour:
        for p in pokemon_locations:
            if p == n:
                count+=1
    replace_character_at_index(game,index,count)
    return count
def check_win(game, pokemon_locations):
    '''victory checking'''
    count = 0
    for g in game:
        if g == FLAG:
            count+=1
    if count == len(pokemon_locations) and UNEXPOSED not in game:
        for p in pokemon_locations :
            if game[p] == FLAG:
                return True
    else:
        return False
def big_fun_search(game, grid_size, pokemon_locations, index):
    '''recursive algorithm 3 lists used for calculate the non-zero pokemon cells'''
    queue = [index]
    discovered = [index]
    visible = []

    if game[index] == FLAG:
        return game
    number = number_at_cell(game, pokemon_locations, grid_size, index)
    game = replace_character_at_index(game,index,number)
    if number != 0:
        return game
    while queue:
        node = queue.pop()
        for neighbour in neighbour_directions(node, grid_size):
            if neighbour in discovered or neighbour is None or game[neighbour] == FLAG:
                continue
            discovered.append(neighbour)
            if game[neighbour] != FLAG:
                number = number_at_cell(game, pokemon_locations, grid_size, neighbour)
                if number == 0:
                    queue.append(neighbour)
            visible.append(neighbour)
    for v in visible:
        number = number_at_cell(game, pokemon_locations, grid_size, v)
        game = replace_character_at_index(game,v,number)
    return game

def for_pokemon(pokemon_locations,game):
    '''for loop which outputting pokemons when the player is scaring a pokemon

    Parameters:
        (tuple<int>): A tuple containing  indexes where the pokemons are created for the game string.
        game (string): a string represents the clls in the game

    Returns:
        game (string): a string represents the clls in the game

    '''
    for p in pokemon_locations:
        game = replace_character_at_index(game,p,POKEMON)
    return game
def main():
    '''This is the begining of the program'''
    grid_size=int(input("Please input the size of the grid: "))
    number_of_pokemons=int(input("Please input the number of pokemons: "))
    pokemon_locations = generate_pokemons(grid_size, number_of_pokemons)
    game = display(grid_size)
    display_game(game,grid_size)
    while check_win(game, pokemon_locations)==False:
        action=input("\nPlease input action: ")
        if len(action)<1:
            print("That ain't a valid action buddy.")
            display_game(game,grid_size)
        elif action=="h":
            print(HELP_TEXT)
            display_game(game,grid_size)
        elif action[0]=="f" and action[1]==" " and action[2] in ALPHA and action[3] in "1234567890":
            poction = action.partition(" ")
            (flag,space,direction) = poction
            action=direction
            position = parse_position(action, grid_size)
            index = position_to_index(position, grid_size)
            game = flag_cell(game,index)
            display_game(game,grid_size)
        elif "UP" in action or "DOWN" in action or "RIGHT" in action or "LEFT" in action:
            action_fragment = action.partition(" ")
            (action, blank, direction) = action_fragment
            position = parse_position(action, grid_size)
            index_x = position_to_index(position, grid_size)
            index = index_in_direction(index_x, grid_size, direction)
            print(index)
            if index == None:
                continue
            if index in pokemon_locations and game[index]!=FLAG:
                game=for_pokemon(pokemon_locations,game)
                display_game(game,grid_size)
                print("You have scared away all the pokemons.")
                break
            else:
                game = big_fun_search(game, grid_size, pokemon_locations, index)
                display_game(game,grid_size)
        elif action[0] in ALPHA and action[1] in "1234567890":
            position = parse_position(action, grid_size)
            index = position_to_index(position, grid_size)
            if index in pokemon_locations and game[index]!=FLAG:
                game=for_pokemon(pokemon_locations,game)
                display_game(game,grid_size)
                print("You have scared away all the pokemons.")
                break
            else:
                game = big_fun_search(game, grid_size, pokemon_locations, index)
                display_game(game,grid_size)
        elif action==":)":
            print("It's rewind time.")
            pokemon_locations = generate_pokemons(grid_size, number_of_pokemons)
            game = display(grid_size)
            display_game(game,grid_size)
        elif action=="q":
            answer=input("You sure about that buddy? (y/n): ")
            if answer=="y":
                print("Catch you on the flip side.")
                break
            elif answer=="n":
                print("Let's keep going.")
                display_game(game,grid_size)
            else:
                print("That ain't a valid action buddy.")
                display_game(game,grid_size)
        else:
            print("That ain't a valid action buddy.")
            display_game(game,grid_size)
    while check_win(game, pokemon_locations):
        print("You win.")
        break
        

if __name__ == "__main__":
    main()
