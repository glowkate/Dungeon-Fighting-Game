#
#Dungon Fighters
#Kate Brownbill Culmanating Project
#V 1.0
#

import random
import time

#This is defining the diffrent moves
FIREBOLT = 0
FRWD_SWNG = 1
MAGIC_RFCT = 2
MAGIC_SWNG = 3
SHIELD_BASH = 4
NOTHING = 5

#for these, the index represented by the vars for the moves (see above) are used
move_to_txt = ["firebolt", "forward swing", "magic reflect", "magic swing", "shield bash", "nothing"]
user_to_txt = ["Human player", "Agressive computer", "Passive computer", "Copycat computer", "Chaotic computer"]


#This is the win chart, it defines what moves are effective agenst what.
#If a move is in a list, it can be beeten by the key to that list.
win_chart = {}
win_chart[FIREBOLT] = [FRWD_SWNG, MAGIC_SWNG, NOTHING]
win_chart[FRWD_SWNG] = [MAGIC_RFCT, SHIELD_BASH, NOTHING]
win_chart[MAGIC_RFCT] = [FIREBOLT, MAGIC_SWNG, NOTHING]
win_chart[MAGIC_SWNG] = [FRWD_SWNG, SHIELD_BASH, NOTHING]
win_chart[SHIELD_BASH] = [FIREBOLT, MAGIC_RFCT, NOTHING]
win_chart[NOTHING] = []


#fails if every element in the list is not the same
def equal_assert(x, y):
    if not x == y:
        print("----Equal Assert Failed----")
        print(x)
        print(y)
        int("string")
    

#fails if the idem is not in the list
def in_assert(idem, list):
    if idem in list:
        return True
    else:
        print("----In Assert Failed----")
        print(idem)
        print(list)
        int("string")


#this class represents a fighter. A player commands a group of fighters.
#A fighter can take damage, and has a name, some flavor_text, a set hp, attack
#and defence. It can also flag itself as alive or downed
class Fighter():
    #this initalises the fighter, storing everything about the fighter
    def __init__(self, moves, name, ft, hp, attack, defence):
        self.moves = moves #should be a list of the attack constents
        self.name = name #should be a string
        self.ft = ft #should be a string
        self.hp = hp #should be an int
        self.max_hp = hp
        self.attack = attack #should be an int
        self.defence = defence #this should be an int
        self.state = 1 #for the state, 1 is alive, 0 is dead (could add more states so not makeing it bool)
    #this damages the fighter and kills it if the hp drops to 0 or lower
    def damage(self, attack): #the attack var is the attacker's attack stat
        damage = attack - self.defence
        if damage < 1: #attacks may deal no less then 1 damage
            damage = 1
        self.hp -= damage
        if self.hp < 1:
            self.state = 0
    #resets the fighter's health and state
    def restore(self):
        self.hp = self.max_hp
        self.state = 1
        



class Player():
    #this initalises the player
    def __init__(self, user, name, ft):
        self.user = user #an int respresenting who is using it(human is 0, all the difrent ai are 1+)
        self.name = name #a string for the name of the player
        self.ft = ft #a string for the flavor text of the player
        self.counter = -1 #a counter used by various ai types
    #this get's the turn for the player. Team is the team of fighters they have
    #act_opnt is the active oponent(specificly their fighter)
    #returns a tuple: (action(switch : 0, attack : 1, exit: 2), attack(is set to nothing if player switched), current_fighter(is set to the fighter who used the move))
    def get_turn(self, team, act_fighter, act_opnt, opnt_player):
        print("==========" + self.name + "'s turn!" + "==========")
        if self.user == 0:
            turn = self.get_human_turn(team, act_fighter, act_opnt, opnt_player)
            return(turn)
        elif self.user == 1:
            turn = agressive_ai(self.counter, act_fighter)
            return(turn)
        elif self.user == 2:
            turn = passive_ai(self.counter, act_fighter)
        elif self.user == 3:
            turn = copycat_ai(self.counter, act_fighter)
        else:
            turn = random_ai(act_fighter)
        return turn

    #get's a human's turn. Includes promps.
    def get_human_turn(self, team, act_fighter, act_opnt, opnt_player):
        #print("Turn " + str(self.counter))
        turn = -1
        while turn == -1:
            print("Your fighter " + act_fighter.name + " has " + str(act_fighter.hp) + " HP remaining.")
            menu1 = get_menu(["attack", "swap", "info", "exit"], "Select an option.\n[ATTACK] [SWAP] [INFO] [EXIT]\n", "Invalid option, try again.")
            if menu1 == 0:
                #ATTACK
                menu2 = get_attack(act_fighter)
                if not menu2 == -1:
                    attack = menu2
                    return (1, attack, act_fighter)
            elif menu1 == 1:
                #SWAP
                non_acv_team = find_act_team(team, act_fighter)
                #print(len(non_act_team))
                #print(non_act_team[0])
                if len(non_acv_team[0]) < 1:
                    print("You don't have a fighter to swap to!")
                else:
                    #print(team, act_fighter)
                    swap = get_swap(team, act_fighter)
                    if not swap == -1:
                        fighter = swap
                        return (0, NOTHING, fighter)
            elif menu1 == 2:
                #INFO
                menu2 = get_info()
                if not menu2 == 0:
                    print("==========Info==========")
                    do_info(menu2, team, act_fighter, act_opnt, opnt_player)
                    print("========================")
            else:
                #EXIT
                menu2 = get_menu(["yes", "no"], "Are you sure you want to quit? All progress will be lost!\n[YES] [NO]\n", "Please select an option")
                if menu2 == 0:
                    return (2, NOTHING, act_fighter)

    def death_swap(self, team, fighter):
        if self.user == 0:
            print(self.name + ", pick a replacement fighter.")
            fighter = get_forced_swap(team, fighter)
        else:
            fighter = ai_swap(team, fighter)
        return fighter

    def update_counter(self, last_move):
        if self.user == 0:
            if self.counter == -1:
                self.counter = 1
            else:
                self.counter += 1
        else:
            self.counter = last_move
            

                
                    
#The agressive ai will always choose attacks that counter the last move the oponent used. If it can't do this, it will mimic the move the oponent used.
#If it can't do that, it will pick a move a random. If it has two moves that counter the last used move, it will pick one at random. It will not switch.
def agressive_ai(last_move, current_fighter):
    if last_move == -1:
        return (random_ai(current_fighter))
    else:
        agressive_moves = []
        for i in win_chart:
            moves = win_chart.get(i)
            if last_move in moves and i in current_fighter.moves: #if the fighter has the move and the move is strong agenst the last move the user used
                agressive_moves.append(i)
        if len(agressive_moves) == 0: #if it has no agressive moves
            if last_move in current_fighter.moves:
                return(1, last_move, current_fighter)
            else:
                return(random_ai(current_fighter))
        else:
            attack = random.choice(agressive_moves)
            return(1, attack, current_fighter)

#The passive ai will always choose attacks that the last move the oponent used is effective agenst if posible. Otherwise it uses the move they used
#last turn if posible, otherwise they will pick at random
def passive_ai(last_move, current_fighter):
    if last_move == -1:
        return(random_ai(current_fighter))
    else:
        passive_moves = []
        moves = win_chart.get(last_move)
        for x in moves:
            if x in current_fighter.moves:
                passive_moves.append(x)
        if len(passive_moves) == 0: #if it has no passive moves
            if last_move in current_fighter.moves:
                return(1, last_move, current_fighter)
            else:
                return(random_ai(current_fighter))
        else:
            attack = random.choice(passive_moves)
            return(1, attack, current_fighter)

#The copycat ai trys to pick the same move that the oponent used last turn. If it can't do so, it picks a
#move that beets similer attacks as the last move the oponent used. Outherwise it picks at random   
def copycat_ai(last_move, current_fighter):
    if last_move == -1:
        return(random_ai(current_fighter))
    else:
        if last_move in current_fighter.moves:
            return (1, last_move, current_fighter)
        else:
            last_win = win_chart.get(last_move)
            copy_moves = []
            for i in current_fighter.moves:
                #print(i)
                move_win = win_chart.get(i)
                for x in move_win:
                    #print("----------------------------")
                    #print(move_win)
                    #print(x)
                    #print(last_win)
                    if x in last_win and not x == NOTHING: #if a move has multipul counters in common with the last move, it increases the odds of that being picked
                        copy_moves.append(i)
            if len(copy_moves) == 0:
                return(random_ai(current_fighter))
            else:
                return(1, random.choice(copy_moves), current_fighter)

#An ai that always attacks using a random attack
def random_ai(current_fighter):
    attack = random.choice(current_fighter.moves)
    return (1, attack, current_fighter)

#the valid options (list of strings), the prompt (string), and the error message (string)
def get_menu(optns, prmpt, error):
    ans = raw_input(prmpt).lower().strip()
    while not ans in optns:
        print(error)
        ans = raw_input(prmpt).lower().strip()
    pos = optns.index(ans)
    return pos #returns the index of the ansure the user input

def get_attack(act_fighter):
    moves = act_fighter.moves
    moves_str = []
    moves_str.append("back") #the back command will always be at the front so the program can reconsise it
    for i in moves: #this grabs the text versons of the moves, not the int verson
        moves_str.append(move_to_txt[i])
    prompt = create_prompt(moves_str)
    menu = get_menu(moves_str, "Please select a move\n" + prompt + "\n", "You don't have that move.")
    if menu == 0: #if they input "back"
        return -1
    else:
        menu = menu - 1
    attack = moves[menu]
    return (attack)

def get_swap(team, acv_fighter):
    non_acv_team = find_act_team(team, acv_fighter)
    options = non_acv_team[1]
    options.insert(0, "back")
    prompt = create_prompt(non_acv_team[1])
    menu = get_menu(non_acv_team[1], "Select a fighter.\n" + prompt + "\n", "That's not a fighter you can swap to!")
    if menu == 0:
        return -1
    else:
        menu = menu -1
    fighter = non_acv_team[0][menu]
    return fighter

def get_forced_swap(team, acv_fighter):
    non_acv_team = find_act_team(team, acv_fighter)
    options = non_acv_team[1]
    prompt = create_prompt(non_acv_team[1])
    menu = get_menu(non_acv_team[1], "Select a fighter.\n" + prompt + "\n", "That's not a fighter you can swap to!")
    fighter = non_acv_team[0][menu]
    return fighter

def find_act_team(team, act_fighter):
    non_acv_team = []
    non_acv_team_names = []
    for i in team: #gathers the fighters you can swap too (everyone who is alive and not your current fighter)
        if i != act_fighter and i.state != 0:
            non_acv_team.append(i)
            non_acv_team_names.append(i.name.lower().strip())
    return (non_acv_team, non_acv_team_names)
    
def ai_swap(team, acv_fighter):
    non_acv_team = []
    for i in team:
        if i != acv_fighter and i.state != 0:
            non_acv_team.append(i)
    fighter = non_acv_team[0]
    return fighter

def get_info(): #get's input from the player on what info they want
    menu = get_menu(["back" ,"my team", "my fighter", "enemy fighter", "enemy player", "moves"], "What do you want to learn about?\n[BACK] [MY TEAM] [MY FIGHTER] [ENEMY FIGHTER] [ENEMY PLAYER] [MOVES]\n", "You can't get info for that.")
    return menu
    
def create_prompt(lst): #creates a menu prompt string like so: [ITEM 1] [ITEM 2] [ITEM 3]...\
    prompt = ""
    for i in lst:
        prompt = prompt + " [" + str(i).upper() + "]"
    return prompt

def create_moves(number):
    moves = [FIREBOLT, FRWD_SWNG, MAGIC_RFCT, MAGIC_SWNG, SHIELD_BASH]
    random.shuffle(moves)
    set = []
    for i in range(number):
        set.append(moves.pop())
    return set

#runs check functions depending on menu's value
def do_info(menu, your_team, your_fighter, enemy_fighter, enemy_player):
    if menu == 1:
        print("Your team:")
        check_team(your_team)
    elif menu == 2:
        print("Your fighter:")
        check_fighter(your_fighter)
    elif menu == 3:
        print("Enemy fighter:")
        check_fighter(enemy_fighter)
    elif menu == 4:
        print("Enemy player:")
        check_player(enemy_player)
    elif menu == 5:
        print("Moves:")
        check_moves()

#prints importent info about a fighter
def check_fighter(fighter):
        print("Name: " + fighter.name)
        print(fighter.ft)
        print("HP: " + str(fighter.hp))
        print("Attack: " + str(fighter.attack))
        print("Defence: " + str(fighter.defence))
        m = ""
        for i in fighter.moves:
            m = m + " " + move_to_txt[i] + ","
        m = m[:-1]
        print("Moves:" + m)

#prints importent info about a team
def check_team(team):
    for i in team:
        print("===============")
        check_fighter(i)
        if i.state == 0:
            print("Unconscious")
        if i.state == 1:
            print("Conscious")
        

#prints importent info about a player
def check_player(player):
    print("Name: " + player.name)
    print(player.ft)
    print("Player type: " + user_to_txt[player.user])

def check_moves():
    print("Firebolt is good agesnt foraward swing and magic swing.")
    print("Forward swing is good agenst shield bash and magic reflect.")
    print("Magic reflect is good agenst firebolt and magic swing.")
    print("Magic swing is good agenst forward swing and shield bash.")
    print("Shield bash is good agenst firebolt and magic reflect.")

#checks to see if any members on the team are alive
def test_alive(team):
    alive = False
    for i in team:
        #print i.state
        if i.state != 0:
            alive = True
        #print(alive)
        #print("----------")
    return alive

#calculates the winner baced on their attacks
#returns 1 if attack1 wins, returns attack2 if attack2 wins, retunrs 0 if tie
def calc_winner(attack1, attack2):
    win_chart1 = win_chart.get(attack1)
    win_chart2 = win_chart.get(attack2)
    if attack1 in win_chart2:
        return 2
    elif attack2 in win_chart1:
        return 1
    else:
        return 0


#attack, fighter object, attack, fighter object
#returns the two fighters
def do_attack(attack1, user1, attack2, user2):
    winner = calc_winner(attack1, attack2)
    win = 0
    loss = 0
    if winner == 1:
        print(user1.name + " won the engagement!")
        hp = user2.hp
        user2.damage(user1.attack)
        new_hp = user2.hp
        damage = hp - new_hp
        print("Delt " + str(damage) + " damage to " + user2.name + ".")
        #print(user2.state)
        if user2.state == 0:
            print(user2.name + " fell unconscious.")
    elif winner == 2:
        print(user2.name + " won the engagement!")
        hp = user1.hp
        user1.damage(user2.attack)
        new_hp = user1.hp
        damage = hp - new_hp
        print("Delt " + str(damage) + " damage to " + user1.name + ".")
        #print(user1.state)
        if user1.state == 0:
            print(user1.name + " fell unconscious.")
    else:
        print("Nither side could gain the upper hand!")
    return (user1, user2)


def do_battle(teem1, teem2, player1, player2):
    act_f1 = teem1[0]
    act_f2 = teem2[0]
    p1_name = player1.name
    p2_name = player2.name
    player1.update_counter(-1)
    player2.update_counter(-1)
    winner = 0
    print(p1_name + ", and " + p2_name + " began to battle!")
    time.sleep(3)
    print("==========" + p1_name + "'s fighter==========")
    check_fighter(act_f1)
    time.sleep(6)
    print("==========" + p2_name + "'s fighter==========")
    check_fighter(act_f2)
    time.sleep(6)
    while winner == 0:
        #This section of code checks if any fighters are down, and swaps them out.
        #print(act_f1.state)
        #print(act_f2.state)
        if act_f1.state == 0:
            if test_alive(teem1) == False:
                print(p2_name + " has won!")
                winner = 2
                return winner
            else:
                act_f1 = player1.death_swap(teem1, act_f1)
                print(p1_name + " sent out " + act_f1.name)
                time.sleep(4)
                print("==========" + p1_name + "'s new fighter==========")
                check_fighter(act_f1)
                time.sleep(6)
        if act_f2.state == 0:
            if test_alive(teem2) == False:
                print(p1_name + " has won!")
                winner = 1
                return winner
            else:
                act_f2 = player2.death_swap(teem2, act_f2)
                print(p2_name + " sent out " + act_f2.name)
                time.sleep(4)
                print("==========" + p2_name + "'s new fighter==========")
                check_fighter(act_f2)
                time.sleep(6)

        #This section of code gets each player's move
        turn1 = player1.get_turn(teem1, act_f1, act_f2, player2)
        if turn1[0] == 2:
            winner = -1
            return winner
        #time.sleep(3)
        turn2 = player2.get_turn(teem2, act_f2, act_f1, player1)
        #time.sleep(3)
        #this handles the exiting
        if turn1[0] == 2 or turn2[0] == 2:
            winner = -1
            return winner
        elif winner == 0:
            #print("==========Results==========")
            
            #this handles the swaping
            if turn1[0] == 0:
                print(p1_name + " withdrew " + act_f1.name)
                act_f1 = turn1[2]
                print(p1_name + " sent out " + act_f1.name)
            if turn2[0] == 0:
                print(p2_name + " withdrew " + act_f2.name)
                act_f2 = turn2[2]
                print(p2_name + " sent out " + act_f2.name)
            #this handles the attacking
            if turn1[0] == 1:
                print(p1_name + "'s fighter " + act_f1.name + " used " + move_to_txt[turn1[1]])
            if turn2[0] == 1:
                print(p2_name + "'s fighter " + act_f2.name + " used " + move_to_txt[turn2[1]])
            #this handles damage
            fighters = do_attack(turn1[1], act_f1, turn2[1], act_f2)
            teem1[teem1.index(act_f1)] = fighters[0] # updates the fighters in the list
            teem2[teem2.index(act_f2)] = fighters[1]
            player1.update_counter(turn2[1])
            player2.update_counter(turn1[1])
            time.sleep(5)
 
 
def heal_team(team):
    for i in team:
        i.restore()
    
#Crall and shut down the portle to hell!
def do_dungeon_crawl():
    bf1 = Fighter([FRWD_SWNG, SHIELD_BASH, MAGIC_SWNG],"Bob", "A simpleminded fighter.", 5, 3, 2)
    bf2 = Fighter([FIREBOLT, MAGIC_RFCT, SHIELD_BASH], "Magios", "A mage who weilds a protective sheild.", 4, 4, 2)
    bf3 = Fighter([FRWD_SWNG, MAGIC_SWNG, MAGIC_RFCT], "Kyrin", "A fragile arcane rouge who deals devistaiting blows.",  3, 6, 1)
    party = [bf1, bf2, bf3]
    print("Welcome to dungeon crawl mode.")
    print("Please select a name for your adventurer.")
    name = raw_input()
    player = Player(0, name, "The leader of a legendary party of adventurers.")
    a1 = make_temple()
    a2 = make_caverns()
    a3 = make_hell()
    world = [a1, a2, a3]
    print("==========REMEMBER==========")
    print("It is a good idea to constently")
    print("check the INFO about both the moves")
    print("the enemy fighter, and your team")
    print("============================")
    time.sleep(4)
    for a in world:
        print("Now entering: " + a[0])
        time.sleep(2)
        print(a[1])
        time.sleep(3)
        for t in a[5]:
            re_try = True
            while re_try == True:
                print("====================")
                print("Now battling " + t[0].name)
                time.sleep(2)
                result = do_battle(party, t[1], player, t[0])
                heal_team(party)
                player.update_counter(-1)
                if result == -1:
                    return -1
                elif result == 2:
                    print("You have been defeated.")
                    ans = get_menu(["yes", "no"], "Will you try again?\n[YES] [NO]\n", "Please select a valid option.")
                    ans = 0
                    if ans == 0:
                        print("Very well...")
                        
                    else:
                        print("Then the world will fall into darkness.")
                        time.sleep(2)
                        return -1
                else:
                    print("Battle passed!")
                    re_try = False
                    time.sleep(2)
        print(a[2])
        time.sleep(6)
        print(a[3])
        time.sleep(6)
        party.append(a[4])
    print("Reluctently. you agree.")
    print("You have cleared Dungeon Crawl mode and shut down the portle to hell!")
    return 1
                    
    
    
def make_temple():
    #tutorial
    p1 = Player(1, "The Temple Defences", "A group of mechs protecting the temple.")
    f1a = Fighter([FRWD_SWNG], "Battle Bot A", "A robot incapable of using anything outher then forward swing. Try using Firebolt or Magic Swing!", 2, 2, 0)
    f1b = Fighter([MAGIC_SWNG], "Battle Bot B", "A robot of incapable of using anything outher then magic swing. Try using Firebolt or Magic Reflect", 2, 2, 0)
    f1c = Fighter([SHIELD_BASH], "Battle Bot C", "A robot of incapable of using anything outher then shield bash. Try using Magic Swing or Forward Swing", 2, 2, 0)
    f1d = Fighter([MAGIC_RFCT], "Battle Bot D", "A robot of incapable of using anything outher then magic reflect. Try using Forward Swing or Sheild Bash", 2, 2, 0)
    f1e = Fighter([FIREBOLT], "Battle Bot E", "A robot of incapable of using anything outher then firebolt. Try using Sheild Bash or Magic Reflect", 2, 2, 0)
    t1 = (p1, [f1a, f1b, f1c, f1d, f1e])
    
    #mummy fight
    p2 = Player(2, "The Mummy Gang", "A shy, pairing of mummys who are doing a favor for the temple guardiens.")
    f2a = Fighter([FRWD_SWNG, SHIELD_BASH], "Sarah the Mummy", "A mummy deaply in love with David. She's returning a favor to the temple guardiens.", 3, 3, 1)
    f2b = Fighter([FIREBOLT, MAGIC_RFCT], "David the Mummy", "A mummy deaply in love with Sarah. He's protecting her unconscious body.", 3, 4, 0)
    t2 = (p2, [f2a, f2b])
    
    #the temple guardians
    p3 = Player(1, "The Temple Guardiens", "A group of robots controlled by ancent spirits.")
    f3a = Fighter([FRWD_SWNG, MAGIC_SWNG], "Slasher", "The spirit inside this mech loves blades.", 2, 5, 0)
    f3b = Fighter([FIREBOLT, MAGIC_RFCT], "Sparky", "The spirit inside this mech has studyed magic.", 3, 3, 1)
    f3c = Fighter([SHIELD_BASH, MAGIC_SWNG], "Scaredy", "The spirit inside this mech is overly protective", 5, 1, 1)
    t3 = (p3, [f3a, f3b, f3c])
    
    #the boss guardian
    p4 = Player(3, "Program X", "The last defence protecting the temple's tresure.")
    p4a = Fighter([FRWD_SWNG, SHIELD_BASH, MAGIC_SWNG], "The Guardian", "The ultimate wepon used by program X.", 4 ,3 ,3)
    t4 = (p4, [p4a])
    
    #area name, area text, and new fighter
    area_name = "Temple"
    begin_text = "You have gathered your best adventurers, ahead of you is a temple that holds a specacular tresure. Holding your head up high, you charge the temple."
    end_text = "As you entered the inner temple, a tall necromancer clad in dark robes turned around to face you. In his hands was the very tresure you were seeking. Smiling, he desends into the caverns below."
    new_fighter_txt = "Behind you, a fluffy air elementle with a bow on her head floats over to you. 'You going after that necromancer? You might need a hand down there! I would be happy to help!'"
    af = Fighter([FIREBOLT, MAGIC_RFCT, MAGIC_SWNG], "Puff", "An air elementle made of clouds. She's an expert at magic.", 4, 5, 1)
    
    #putting togeather everything
    area_info = (area_name, begin_text, end_text, new_fighter_txt, af, [t1, t2, t3, t4])
    return area_info
    
    
def make_caverns():
    #elementle force
    p1 = Player(2, "The Native Elementles", "Elementles who are native to the area. They're protecting their teritory.")
    f1a = Fighter([FRWD_SWNG, MAGIC_RFCT], "Lesser Water Elementle", "A young water elementle weilding a magical staff.", 5, 1, 1)
    f1b = Fighter([FRWD_SWNG, SHIELD_BASH], "Lesser Earth Elementle", "A young earth elementle who uses their own body to attack.", 4, 2, 1)
    f1c = Fighter([FRWD_SWNG, MAGIC_RFCT, SHIELD_BASH], "Water Elementle", "A water elementle who carrys a shield.", 6, 2, 2)
    t1 = (p1, [f1a, f1b, f1c])
    
    #invaiding undead 
    p2 = Player(1, "The Invading Undead", "A group of undead who are being forced to fight by the necromancer.")
    f2a = Fighter([FIREBOLT, MAGIC_RFCT], "Wisp", "A spirit bound to a skull.", 3, 3, 1)
    f2b = Fighter([SHIELD_BASH, FRWD_SWNG], "Shadow", "The re-animated shadow of a dead adventurer", 3, 1, 3)
    f2c = Fighter([FIREBOLT, MAGIC_SWNG, MAGIC_RFCT], "Specter", "A wisp given the more solid form of a rugged, hooded cloak", 4, 4, 2)
    f2d = Fighter([SHIELD_BASH, FRWD_SWNG, MAGIC_SWNG], "Imp's Shadow", "The re-animated shadow of an imp from hell.", 4, 2, 4)
    t2 = (p2, [f2a, f2b, f2c, f2d])
    
    #the corrupted
    p3 = Player(3, "The Corrupted Elementles", "A group of elementles corrupted by the necromancer.")
    f3a = Fighter([FRWD_SWNG, SHIELD_BASH, MAGIC_SWNG], "Corrupted Water Elementle", "A water elementle corrupted by necrodic energies.", 5, 3, 2)
    f3b = Fighter([FRWD_SWNG, SHIELD_BASH, MAGIC_SWNG], "Infested Earth Elementle", "An earth elementle infested and controlled by Corpse Mushrooms.", 6, 3, 1)
    f3c = Fighter([FRWD_SWNG, SHIELD_BASH, MAGIC_RFCT], "Corrupted Earth Elementle", "An earth elementle corrupted by necrodic energies.", 5, 4, 1)
    t3 = (p3, [f3a, f3b, f3c])
    
    #the necromancer
    p4 = Player(1, "The Dark Necromancer", "The leader of the undead.")
    f4a = Fighter([FIREBOLT, FRWD_SWNG, MAGIC_RFCT], "Dark Necromancer", "Once a powerful imp, The Dark Necromancer betrayed his supiriors and eternal undeath was his punishment.", 5, 5, 3)
    t4 = (p4, [f4a])
    
    #area details
    area_name = "Caverns"
    begin_text = "Delving into the caverns below the temple, a cold brease blows through the air. The powers of undeath threatens to overwelm the native elementles."
    end_text = "After defeating the Dark Necromancer, a deafing sound screached through the air. A portal leading to hell thrust open. If it alowed to exist, it could threaten to distroy the mortal world."
    new_fighter_txt = "One of the specters who previosly was under control of the Dark Necromancer aproched you. 'I might be undead but I still care about this world, if you're going to be fighting the armys of hell then I'll help you.'"
    af = Fighter([FRWD_SWNG, MAGIC_RFCT, SHIELD_BASH], "Eve", "A specter who will do anything to protect her world.", 5, 3, 2)
    
    #returning stuff
    area_info = (area_name, begin_text, end_text, new_fighter_txt, af, [t1, t2, t3, t4])
    return area_info
    
def make_hell():
    #'field trip'    
    p1 = Player(2, "Ti'carr the Teacher", "She's taking her demonic students on a little 'feild trip' to teach them combat skills")
    f1a = Fighter([MAGIC_SWNG, FRWD_SWNG], "Young Imp", "A young imp attending combat school. Is hoping to hang out with his friends after this.", 3, 2, 2)
    f1b = Fighter([MAGIC_RFCT, FIREBOLT], "Young Echolo", "A very friendly, batlike demon who relys on echolocation to see.", 4, 1, 2)
    f1c = Fighter([FRWD_SWNG, FIREBOLT], "Young Spiker", "A frail but powerful spiderlike demon. Aspires to be an assissan someday.", 3, 4, 0)
    f1d = Fighter([FIREBOLT, MAGIC_SWNG, SHIELD_BASH], "Fire Elementle", "A fire elementle hired to protect Ti'carr incase the worst happened.", 3, 4, 3)
    t1 = (p1, [f1a, f1b, f1c, f1d])
    
    #The assissans
    p2 = Player(2, "The Assasins", "Two assasins payed by some unknown demon")
    f2a = Fighter([FRWD_SWNG, FIREBOLT, MAGIC_SWNG], "Apprentice Spiker", "An apprentice spiker running a job as an assasin with her employer.", 4, 6, 0)
    f2b = Fighter([FRWD_SWNG, FIREBOLT, MAGIC_SWNG], "Elite Spiker", "An elite spiker training fellow spikers as assasins.", 5, 6, 2)
    t2 = (p2, [f2a, f2b])
    
    #The knights
    p3 = Player(1, "The Imp Lord", "The imp lord commanding a leagon of hell knights.")
    f3a = Fighter([MAGIC_SWNG, FRWD_SWNG, MAGIC_RFCT], "Imp Knight", "His pointed tail is now long enouth and sharp enouth to act as a wepon.", 5, 4, 4)
    f3b = Fighter([MAGIC_SWNG, FRWD_SWNG, SHIELD_BASH], "Echolo Knight", "If not for their extreme loyalty to hellish powers, these batlike people likely wouldn't been seen as a demon due to their raw kindness.", 6, 4, 3)
    f3c = Fighter([FIREBOLT, MAGIC_SWNG, SHIELD_BASH], "Fire Knight", "A greater elementle who works as a knight. Most demons see her as a lesser being.", 5, 5, 3)
    t3 = (p3, [f3a, f3b, f3c])
    
    #The Imp Lord
    p4 = Player(1, "The Imp Lord", "The imp lord, here to defeat you once and for all.")
    f4a = Fighter([MAGIC_SWNG, FRWD_SWNG, MAGIC_RFCT, FIREBOLT], "Dar", "The lord of imps, the ruler of hell.", 7, 5, 4)
    t4 = (p4, [f4a])
    
    #area details
    area_name = "Hell"
    begin_text = "Passing through the portal to hell, the landscape changes durasticly. The sky is a chaotic mess of purples and greens. The hot, dry air leaves you constently thirsty."
    end_text = "As Dar the demon lord falls to the ground, you open the door to the inner sanctum where a large crystle poweres the rift between worlds. Distroying it would close the rift and save your world, but it would trap you here. Eve urges you to distroy it, Magios interupts her. The whole party erupts in argument."
    new_fighter_txt = "While your party is arguing, an Echolo tugs at your shirt. 'Hey uh...I have a friend who wanted to-' an implike jester came through the door with a big smile. 'Fellas, fellas...we can make a compramise here. I'll tell you this, I'm one of the most powerful demons in hell. If I tellaport you home, after you shut down the portle, I won't ask much of you. All I'd ask for is for entertainment. Anytime you wish, you can take my chalenge, at no risk you yourself even! So, what do you say?'"
    af = Fighter([MAGIC_SWNG, FRWD_SWNG, FIREBOLT], "Echa", "An echolo who wants to explore the mortle world.", 4, 4, 2)
    
    #return time
    area_info = (area_name, begin_text, end_text, new_fighter_txt, af, [t1, t2, t3, t4])
    return area_info
    
            
def jester_game():
    player = Player(0 ,"JESTER", "IT'S ME, IT'S YOU")
    him = Fighter([FIREBOLT, FRWD_SWNG, MAGIC_SWNG, SHIELD_BASH, MAGIC_RFCT], "The Demonic Joker", "A sub-speaces of imp who is arguably the most powerful being in existence", 6, 6, 6)
    lv = get_menu(["1", "2", "3", "4"], "Pick a dificalty level.\n[1] [2] [3] [4]\n", "That's not a valid levle.")
    foe = Player(4, "THE ENEMY", "BORING")
    team = []
    for i in range(lv + 1):
        black_moves = []
        red_moves = []
        while black_moves == red_moves:
            black_moves = create_moves(4)
            red_moves = create_moves(4)      
        card_black = Fighter([MAGIC_RFCT, FRWD_SWNG, SHIELD_BASH, MAGIC_SWNG], "Dark Card", "Woven from shadow. Does it even exist?", 3 + i, 3 + i, 1 + i)
        card_red = Fighter([MAGIC_RFCT, FIREBOLT, MAGIC_SWNG, SHIELD_BASH], "Red Card", "Woven from blood. Does it even exist?", 3 + i, 4 + 1, 0 + 1)
        team.append(card_black)
        team.append(card_red)
    do_battle([him], team, player, foe)
            
menu = True
jester = False           
while menu == True:
    if jester == False:
        ans = get_menu(["dungeon crawl", "tutorial", "exit", "jevil"], "Pick a game mode\n[DUNGEON CRAWL] [TUTORIAL] [EXIT]\n", "Please pick a valid mode")
    else:
        ans = get_menu(["dungeon crawl", "tutorial", "exit", "jevil", "jester's game"], "Pick a game mode\n[DUNGEON CRAWL] [TUTORIAL] [JESTER'S GAME] [EXIT]\n", "Please pick a valid mode")
    if ans == 0:
        result = do_dungeon_crawl()            
        if result == 1:
            jester = True
    elif ans == 1:
        print("\nWelcome to dungeon fighters!")
        print("Here you command a party of adventurers who fight various foes.")
        print("There are 5 moves, FIREBOLT, FORWARDS SWING, MAGIC SWING")
        print("SHIELD BASH, and MAGIC REFLECT. Every fighter has some")
        print("combanation of moves. Once the two fighters have picked a move")
        print("to use, the two fight. Depending on what moves they used, one")
        print("fighter will gain the advantage in the battle and deal damage.")
        print("\nEach fighter as 3 stats: HP ATTC DEF. HP is the hit points")
        print("ATTC is linked directly to damage given by a fighter. DEF absorbs")
        print("damage given by an oponent, however DEF will not compleatly absorb")
        print("all the damage.\n")
    elif ans == 2:
        menu = False
    elif ans == 3:
        jester = True
        print("Jester's game unlocked")
    elif ans == 4:
        jester_game()
        

#---------------------------UNITTESTING-------------------------
def test_ai():
    fighter1 = Fighter([FIREBOLT, MAGIC_SWNG], "fighter1", "a fighter", 1, 1, 1)
    fighter2 = Fighter([SHIELD_BASH, FRWD_SWNG, MAGIC_SWNG], "fighter2", "a fighter", 1, 1, 1)
    
    turnA1 = agressive_ai(SHIELD_BASH, fighter1) #should return magic swing
    turnA2 = agressive_ai(FIREBOLT, fighter2) #should return sheild bash
    turnP1 = passive_ai(SHIELD_BASH, fighter1) #should return firebolt
    turnP2 = passive_ai(SHIELD_BASH, fighter2) #should return sheild bash
    turnC1 = copycat_ai(FRWD_SWNG, fighter1) #should return magic swing
    turnC2 = copycat_ai(FRWD_SWNG, fighter2) #should return forward swing
    
    equal_assert(turnA1, (1, MAGIC_SWNG, fighter1))
    equal_assert(turnA2, (1, SHIELD_BASH, fighter2))
    equal_assert(turnP1, (1, FIREBOLT, fighter1))
    equal_assert(turnP2, (1, SHIELD_BASH, fighter2))
    equal_assert(turnC1, (1, MAGIC_SWNG, fighter1))
    equal_assert(turnC2, (1, FRWD_SWNG, fighter2))

def test_damage():
    fighter1 = Fighter([FRWD_SWNG], "fighter1", "a fighter", 2, 1, 1)
    fighter2 = Fighter([FRWD_SWNG], "Fighter2", "A fighter", 2, 1, 0)
    fighter3 = Fighter([FRWD_SWNG], "Fighter3", "a fighter", 1, 1, 0)

    fighter1.damage(2) #state should be 1, hp should be 1
    fighter2.damage(2) #state should be 0, hp should be 0
    fighter3.damage(1) #state should be 0, hp should be 0
    
    equal_assert(fighter1.hp, 1)
    equal_assert(fighter2.hp, 0)
    equal_assert(fighter3.hp, 0)
    
    equal_assert(fighter1.state, 1)
    equal_assert(fighter2.state, 0)
    equal_assert(fighter3.state, 0)

def test_restore():
    fighter1 = Fighter([FRWD_SWNG], "Fighter1", "A fighter", 8, 1, 0)
    fighter2 = Fighter([FRWD_SWNG], "Fighter1", "A fighter", 2, 1, 0)
    
    fighter1.damage(4)
    fighter2.damage(4)
    
    fighter1.restore()
    fighter2.restore()
    
    equal_assert(fighter1.hp, 8)
    equal_assert(fighter2.state, 1)
    
    equal_assert(fighter2.hp, 2)
    equal_assert(fighter2.state, 1)

equal_assert(1, 1)
equal_assert(2, 2)
test_ai()
test_damage()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
