import discord
from discord.ext import commands

from time import sleep
from time import strftime, gmtime
from os import listdir
import os
import random
import asyncio
import threading
from contextlib import suppress
from nltk import word_tokenize 

channel_bind = ''
help_dict = {}

g_holder = {}
roles_list = []
roles_dict = {}
players_list = []
players_dict = {}

slots = 0
lock = False
status_dict = {}
vote_dict = {}

CONS_roles_list = []                    #A constant roles_list chosen after a game starts
STNDRD_roles_list = ['villager', 'witch', 'guardian', 'tree', 'hunter', 'cupid', 'wolf', 'elder']   #A constant roles_list contains available roles in the mode
prevsavi = ''                           #Name of the previous prey of the hunter
db_time = 30                            #Debate time (secs) (Note that the db_time's value means nothing. Tt's just a sample and will be reset once the timer's used.)
PHASE = 'n/a'
DAY = 0
vote_board = '```n/a```'                      #A board displays players and the votes for them
GM = 'Cli'
GM_dict = {}

client = commands.Bot(command_prefix = '-')
client.remove_command('help')

@client.event
async def on_ready():
    help_dict_plugin()
    await client.change_presence(game=discord.Game(name='with aknalumos <3'))
    print("|||||   THE WOLF IS READY   |||||")

@client.event
async def on_message(message):
    global channel_bind

    #Check if the message.channel == channel.bind
    if channel_bind:
        if message.channel.name != channel_bind: return
    if message.author == client.user:
        return
    if message.author.bot: return
    await client.process_commands(message)



class player:
    role = ''
    lives = 1
    call_pass = True
    status = True

    lover = ''
    prey = ''

    heal_pod = 1
    kill_pod = 1

    def __init__(self, name):
        self.name = name
        

@client.command(pass_context=True)
async def help(ctx, *args):
    global help_dict
    global STNDRD_roles_list
    raw = []
    help_key = ''

    #Get specific help key
    for word in args:
        raw.append(word)
    help_key = ''.join(raw)
    
    box = discord.Embed(
        title = '**K A L E I D O S C O P E    C L I**',
        description = """A wolf, cute one.
                         ______ ______ ______ ______ ______ ______ """,
        colour = discord.Colour(0x011C3A)
    )
    #Determine which help page should be displayed
    if help_key == '':
        box.set_thumbnail(url='https://cdn.discordapp.com/avatars/449278811369111553/d4a3085e1b4a9b77d51abf8da3ebcc22.jpg')
        box.add_field(name='Werewolf', value='`help` `cast` `bind` `unbind` `assign` `resign` `setcard` `stop` `skip` `vote` `stt` `addtime`', inline=False)
        box.add_field(name='Config', value="""`bind` `unbind`""", inline=False)
        box.add_field(name="Rules, Functions and FAQ about the game", value="`rnr`")
        box.set_footer(text="use `-help <command>` for more info about the command.")
        await client.say(embed=box)
    elif help_key in list(help_dict.keys()):
        box_small = discord.Embed(
            title = f'**-{help_key}**',
            description = f"{help_dict[help_key]}",
            colour = discord.Colour(0x011C3A)
        )
        await client.say(embed=box_small)
    elif raw[0] == 'rnr':
        try:
            if raw[1].lower() in STNDRD_roles_list:
                try:
                    await client.send_file(ctx.message.channel, f"roles_help/{raw[1]}.png", content=f"Roles: **{raw[1].upper()}**")
                except: print("FILE NOT FOUND!")
            elif raw[1].lower() == 'gm':
                with open('roles_help/gm.txt', 'r', encoding='utf-8-sig') as g:
                    box_small = discord.Embed(
                        title = '**:ledger: G A M E  M A S T E R**',
                        description = f"{g.read()}",
                        colour = discord.Colour(0x011C3A)
                    )
                await client.say(embed=box_small)
            elif raw[1].lower() == 'faq':
                with open('rules_help/faq.txt', 'r', encoding='utf-8-sig') as f:
                    box_small = discord.Embed(
                        title = '**:ledger: F A Q**',
                        description = f"{f.read()}",
                        colour = discord.Colour(0x011C3A)
                    )
                await client.say(embed=box_small)
        except IndexError:
            box_small = discord.Embed(
                title = '**R U L E S  \'N  R O L E S  **',
                description = "______ _______ ________ ________ ________ _______",
                colour = discord.Colour(0x011C3A)
            )
            box_small.add_field(name="Thư mục postfix", value="`rnr` + [`<role>` | `gm` | `faq`]")
            box_small.add_field(name='______ _______ ________ ________ ________ _______', value="from blog __LuatMaSoi__ | [LUẬT CHƠI MA SÓI Việt Hóa Mở Rộng](http://luatmasoi.blogspot.com/2017/05/huong-dan-luat-ma-soi-viet-hoa-mo-rong.html)", inline=False)
            await client.say(embed=box_small)
    else:
        await client.say(":warning: Please only use one of the available commands.")

    

@client.command(pass_context=True)
async def bind(ctx):
    global channel_bind
    if not channel_bind:
        channel_bind = ctx.message.channel.name
        await client.say(f":white_check_mark: Bot's binded to channel {ctx.message.channel.name}!")
    else:
        await client.say(f":warning: Please unbind the bot from text channel <{channel_bind}>")

@client.command(pass_context=True)
async def unbind(ctx):
    global channel_bind
    if channel_bind == ctx.message.channel.name:
        if channel_bind:
            channel_bind = ''
            await client.say(f":white_check_mark: Unbinded from channel {ctx.message.channel.name}!")
        else:
            await client.say(":warning: The bot had already been unbind!")

@client.command(pass_context=True, aliases=['-c'])
async def cast(ctx):
    global roles_list
    global players_list
    global roles_dict
    global players_dict
    global lock
    global slots
    global channel_bind
    global CONS_roles_list
    global db_time
    global PHASE

    if lock == True: 
        await client.say(":upside_down: Game's already been opened!")
        return

    roles_list = ['villager', 'witch', 'guardian', 'tree', 'hunter', 'cupid', 'wolf']
    CONS_roles_list = roles_list.copy()

    #Set the variables back to default
    lock = True
    db_time = 30
    PHASE = 'n/a'
    slots = int(len(roles_list))
    await data_clear_procedure()
    channel_bind = ctx.message.channel.name
    await setup_get()

@client.command(pass_context=True, aliases=['-uc'])
async def uncast(ctx):
    global roles_list
    global players_list
    global roles_dict
    global players_dict
    global lock
    global slots
    global channel_bind
    global CONS_roles_list
    global db_time
    global PHASE

    if lock == False: 
        await client.say(f":upside_down: Game's already been closed {ctx.message.author.name}...")
        return

    #Check if game has started yet
    mode = await game_stt_check()
    if mode == 'on': await client.say(f"They're playing you know, {ctx.message.author.mention} :<"); return

    lock = False
    db_time = 30
    PHASE = 'n/a'
    slots = 0
    await data_clear_procedure()
    roles_list.clear()
    channel_bind = ''
    box = await msg_embe(':tada: **Avada kedavra!** The game is *gone*, oof.', 0x011C3A)
    await client.say(embed=box)

@client.command(pass_context=True)
async def assign(ctx, *args):
    global players_list
    global players_dict
    global GM_dict
    global GM
    global slots
    clc = 0; mode = ''

    #Check if game has started yet
    mode = await game_stt_check()
    if mode == 'on': await client.say(f"Too late, {ctx.message.author.mention} :< Grab some snack and watch them suffer!"); return

    #Check if game's opened or there are any slots left
    if not roles_list:  await client.say(f":x: Maybe there's no game, maybe there's not slot left for you, {ctx.message.author.name}..."); return
    if ctx.message.author.name not in players_list and GM != ctx.message.author.name:
        for i in args:
            if i.lower() == 'gm':
                if not GM_dict:
                    GM_dict['GM'] = ctx.message.author
                    GM = ctx.message.author.name
                    await client.say(f"{ctx.message.author.mention} has been made a **Game Master**!")
                    await setup_get()
                    return
                else: await client.say("Có GM xí chỗ rồi :>"); return
        players_list.append(ctx.message.author.name)
        players_dict[ctx.message.author.name] = ctx.message.author

        #Create setting_up box
        await setup_get()
        #Generate approriate colour
        if len(players_list) == slots: clc = 0xE30F0F  #RED
        else: clc = 0xCBF411
        #Create msg box
        box = discord.Embed(
            title=f"**[**{len(players_list)}/{slots}**] players joined:**   {',  '.join(players_list)}",
            colour = discord.Colour(clc)
        )
        await client.say(embed=box)
    else:
        await client.say("Omae wa've already assigned!")

@client.command(pass_context=True)
async def resign(ctx):
    global players_list
    global players_dict
    global GM
    global GM_dict
    global slots
    clc = 0; stt = ''

    #Check if game's opened or there are any slots left
    if not roles_list:  await client.say(f":x: {ctx.message.author.name}, you can't `-resign` when you've not assigned yet :>"); return
    #Check if the game's already started
    stt = await game_stt_check()
    if stt == 'on': await client.say(f":x: {ctx.message.author.name}, you can't `-resign` during a game! Don't be a thrower..."); return

    if ctx.message.author.name in players_list or GM == ctx.message.author.name:
        if GM == ctx.message.author.name:
            GM_dict.clear()
            GM = 'Cli'
            await client.say(f"{ctx.message.author.mention} is **no longer** a Game Master!")
            return
        players_list.pop(int(players_list.index(ctx.message.author.name)))
        del players_dict[ctx.message.author.name]

        #Create setting_up box
        await setup_get()
        #Generate approriate colour
        if len(players_list) == slots: clc = 0xE30F0F  #RED
        else: clc = 0xCBF411
        #Create msg box
        box = discord.Embed(
            title=f"**[**{len(players_list)}/{slots}**] players joined:**   {',  '.join(players_list)}",
            colour = discord.Colour(clc)
        )
        await client.say(embed=box)
    else:
        await client.say("Omae wa've not joined game yet!")

@client.command(pass_context=True)
async def stop(ctx):
    global lock
    global players_list
    stt = ''

    #Check if the game starts
    stt = await game_stt_check()
    if stt == 'off': await client.say("There's no game to skip!"); return

    #Check if the user is in players_list
    if ctx.message.author.name not in players_list: await client.say(f"{ctx.message.author.mention} you don't flip other's board like that. It's rude :<")
    
    msg = await client.send_message(ctx.message.channel, f":envelope_with_arrow: All `{len(players_list)}` players have to vote the emote to stop the game! (Players=Emotes - 1)")
    await client.add_reaction(msg, '\U00002705')
    while True:
        rea = await client.wait_for_reaction(emoji='\U00002705', timeout=20, message=msg)
        if rea[0].me != client and rea[0].count >= int(len(players_list) + 1):
            await client.say(":heavy_check_mark: Game will stop by the end of the current phase!")
            lock = False
            #lock = False
            #await client.say(":warning: Game will end by the end of the day.")


@client.command(pass_context=True, aliases=['-v'])
async def vote(ctx, *args):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global vote_dict
    global status_dict
    global vote_board
    raw = []
    alive = []

    #Check if the users is a player or is DEAD
    if ctx.message.author.name not in players_list:
        return
    elif status_dict[ctx.message.author.name] == 'DEAD':
        return

    for i in args:
        raw.append(i)

    for p in players_list:
        if status_dict[p] == 'ALIVE':
            alive.append(p)

    try:
        if raw[0] in players_list and status_dict[raw[0]] == 'ALIVE':
            vote_dict[ctx.message.author.name] = raw[0]
            await client.say(f":raised_hand: {ctx.message.author.mention} has voted to hang {players_dict[raw[0]].mention}! --- [{len(list(vote_dict.keys()))}/{len(alive)} total votes received]")       
            #Message to the GM (if available)
            if GM != 'Cli':
                tm = ''
                tm = strftime("%H:%M:%S", gmtime())
                await client.send_message(GM_dict['GM'], f"`{tm}`\t:raised_hand: |\t **{ctx.message.author.name}** has voted to hang {players_dict[raw[0]].mention}! --- [{len(list(vote_dict.keys()))}/{len(alive)} total votes received]")

        else:
            await client.say(f"{ctx.message.author.mention}, please vote a player **in the list** that is **still alive**.")
    except IndexError:
        await client.say(vote_board)

@client.command(pass_context=True, aliases=['-stc'])
async def setcard(ctx, *args):
    global roles_list
    global STNDRD_roles_list
    global CONS_roles_list
    global slots
    global lock
    global GM
    stt = ''; cards = []

    #Check GM authority (if available)
    if GM != 'Cli' and GM != ctx.message.author.name:
        await client.say(f"{ctx.message.author.mention}, bạn không có quyền sử dụng lệnh này khi có GM!")
        return
    if not lock: await client.say(":warning: **No game's currently active!** Use `-create` to make one."); return
    stt = await game_stt_check()
    if stt == 'on': await client.say(":warning: Hey hey no role request **during match**!"); return

    for card in args:
        if card in STNDRD_roles_list:
            cards.append(card)
        else: 
            await client.say(f":x: `{card}` card not available!")
            return
    roles_list = cards.copy()
    CONS_roles_list = roles_list.copy()
    slots = int(len(roles_list))
    await setup_get()

@client.command(pass_context=True, aliases=['+t'])
async def addtime(ctx, *args):
    global db_time
    global PHASE
    sample = 0
    raw = []

    #Check if the current phase is DAY
    if PHASE != 'day': await client.say(":warning: **Daylight**'s required to use this command! :< Mou, have you even joined a game?"); return

    sample = int(db_time)
    for t in args:
        try:
            int(t)
        except ValueError:
            await client.say(":warning: Hey, me stupid, please **give** nothing but an integer >.<")
            return
        raw.append(t)
    sample += int(raw[0])
    if sample > 300:
        await client.say(":warning: You can only say shit for 5 mins (300secs). No more, kay?!")
        return
    else:
        db_time += int(raw[0])
        await client.say(f":white_check_mark: Now you have `{db_time}` secs left to watch your friends suffer <3")

@client.command(pass_context=True)
async def stt(ctx):
    global status_dict
    global players_dict
    global lock
    global GM
    global GM_dict
    global g_holder
    global PHASE
    global DAY
    keys = list(status_dict.keys())
    static =  ''
    board = ''

    lover = ''; prey = ''; pot = ''

    #Check if there's a game
    if not bool(players_dict): await client.say("```There's only dust in this place...```"); return
    
    #GM full status
    if ctx.message.author.name == GM:
        for i in keys:
            
            try:
                if g_holder[i].lover:
                    lover = ''.join([' >Love: ', g_holder[i].lover])
            except: pass
            try:
                if g_holder[i].prey:
                    prey = ''.join([' >Prey: ', g_holder[i].prey])
            except: pass
            try:
                if g_holder[i].role == 'witch':
                    pot = ''.join(['> Heal:', g_holder[i].heal_pod, '> Poison:', g_holder[i].kill_pod])
            except: pass
            
            if status_dict[i] == 'ALIVE':
                static = f"[{status_dict[i]}][ ]"
            elif status_dict[i] == 'DEAD':
                static = f"[ ][{status_dict[i]}]"
            if keys.index(i) == 0 and len(keys) > 1:
                board = f'```md\n**{PHASE.upper()} of Day {DAY}**\n\n{i}    ------------    {static} \n> Roles: {g_holder[i].role}{lover}{prey}{pot}'
            elif keys.index(i) == int(len(keys) - 1):
                if len(keys) > 1:
                    seq = (board, f" \n{i}    ------------    {static}  \nRoles: {g_holder[i].role}{lover}{prey}{pot}```")
                    board = ''.join(seq)
                else:
                    board = f"```md\n**{PHASE.upper()} of Day {DAY}**\n\n{i}    ------------    {static} \n> Roles: {g_holder[i].role}{lover}{prey}{pot}```"
            else:
                seq = (board, f" \n{i}    ------------    {static}")
                board = ''.join(seq)
            #Send status board
            await client.send_message(GM_dict['GM'], board)
            return
    
    #Generate status board msg
    for i in keys:
        
        if status_dict[i] == 'ALIVE':
            static = f"[{status_dict[i]}][ ]"
        elif status_dict[i] == 'DEAD':
            static = f"[ ][{status_dict[i]}]"
        if keys.index(i) == 0 and len(keys) > 1:
            board = f'```md\n{i}    ------------    {static}'
        elif keys.index(i) == int(len(keys) - 1):
            if len(keys) > 1:
                seq = (board, f" \n{i}    ------------    {static}```")
                board = ''.join(seq)
            else:
                board = f"```md\n{i}    ------------    {static}```"
        else:
            seq = (board, f" \n{i}    ------------    {static}")
            board = ''.join(seq)

    #Send status board
    await client.say(board)

@client.command(pass_context=True)
async def starto(ctx):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global PHASE
    global DAY
    global GM
    global GM_dict
    global lock
    global g_holder
    wolf = []; villager = []
    inp = ''

    #Check if there's a GM and the sender's the GM
    if GM != 'Cli' and GM != ctx.message.author.name:
        await client.say(f"{ctx.message.author.mention}, you have no permission to use this command when there's a **GM**!")
        return

    #Check if there's enough players
    if len(players_list) < 1: 
        await client.say("How about we start a game WITH some hooman?!")
        return

    #Randomly assign roles to players
    holder = {name: player(name=name) for name in players_list}
    for i in list(holder.keys()):
        holder[i].role = random.choice(roles_list)
        roles_list.pop(roles_list.index(holder[i].role))
        print(holder[i].role)

        #Lists of wolves and villagers
        if holder[i].role == 'wolf':
            wolf.append(i)
            roles_dict[holder[i].role] = wolf
        elif holder[i].role == 'villager':
            villager.append(i)
            roles_dict[holder[i].role] = villager

        #Give special status to particular roles.
        elif holder[i].role == 'elder':
            holder[i].lives += 1
        else:
            roles_dict[holder[i].role] = i

    #Pass info from holder to g_holder
    g_holder = holder.copy()

    #Inform role for each player
    for name in players_list:    
        await client.send_message(players_dict[name], f":bell: **Your role:** << {holder[name].role} >>")
    #Message names of other wolves for each wolf
    for name in wolf:
        rest = wolf.copy(); rest.remove(name)
        await client.send_message(players_dict[name], f":wolf: You, {' and '.join(rest)} are wolves. Have a good hunt! :wolf: ")

    print(roles_list)
    print(roles_dict)
    print(players_list)
    while lock:
        DAY += 1
        #Update status_dict
        await status_update(holder)

    # NIGHT PHASE
        PHASE = 'night'
        await night(holder)
        if GM == 'Cli':                     #Bot-mode  
            #try:
            await judge(holder)
            #except: pass
        else:                               #GM-mode
            await client.send_message(GM_dict['GM'], f"GM {GM_dict['GM'].mention}, `..next` or `..end` | **New day** or **end** the game.")
            while True:
                inp = await client.wait_for_message(author=GM_dict['GM'])
                if inp.content == '..next' and lock == True:
                    break
                elif inp.content == '..next' and lock == False:
                    await client.send_message(GM_dict['GM'], "All players are ded, please `-end` the game.")
                elif inp.content == '..end':
                    lock = False; break
        if not lock: break
        #Update status_dict
        await status_update(holder)
        g_holder = holder.copy()
    # DAY PHASE        
        PHASE = 'day'
        await day(holder)
        if GM == 'Cli':                     #Bot-mode
            try:
                await judge(holder)
            except: pass
        else:                               #GM-mode
            await client.send_message(GM_dict['GM'], "`..next` or `..end` | **Next day** or **end** the game.")
            while True:
                inp = await client.wait_for_message(author=GM_dict['GM'])
                if inp.content == '..next' and lock == True:
                    break
                elif inp.content == '..next' and lock == False:
                    await client.send_message(GM_dict['GM'], "All players are ded, please `-end` the game.")
                elif inp.content == '..end':
                    lock = False; break           
        if not lock: break
        #Update status_dict
        await status_update(holder)
        g_holder = holder.copy()
    await reveal(holder)
    await data_clear_procedure()
    


async def night(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global prevsavi
    global GM
    global GM_dict
    global lock

    death_bywolf_wish = []
    death_byman_wish = []
    death_byGM_wish = []
    death_list = []
    save_wish = []
    inp1 = ''; raw1 = []
    
    if GM != 'Cli':
        await client.send_message(GM_dict['GM'], content=f":page_facing_up: **Night - DAY {DAY}**")
    await client.say("===========:waxing_gibbous_moon:=== SUN SET, SOON CAME THE MOON ===:waxing_gibbous_moon:============")

    #CUPID - call
    if 'cupid' in list(roles_dict.keys()):
        if holder[roles_dict['cupid']].call_pass:
            box_cupid = await msg_embe("**Cupid wakes up pleasee!!!!**", 0xFED0EE)
            await client.say(embed=box_cupid)
        
            await client.send_message(players_dict[roles_dict['cupid']], "Who do you wanna shoot?")
            rep1 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])
            while rep1.content not in players_list:
                await client.send_message(players_dict[roles_dict['cupid']], ":o: I don't know that guy, is he **in the game**?!")
                rep1 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])

            await client.send_message(players_dict[roles_dict['cupid']], "And who's the next one?")
            rep2 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])
            while rep2.content not in players_list:
                await client.send_message(players_dict[roles_dict['cupid']], ":o: I don't know that guy, is he **in the gam**e?!")
                rep2 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])

            holder[rep1.content].lover = rep2.content
            holder[rep2.content].lover = rep1.content

            #Message to the GM (if available)
            if GM != 'Cli':
                tm = ''
                tm = strftime("%H:%M:%S", gmtime())
                await client.send_message(GM_dict['GM'], f"`{tm}`\t:cupid: |\t **{holder[roles_dict['cupid']].name}** (as *Cupid*) has shot {rep1.content} and {rep2.content}.")

            client.send_message(players_dict[rep1.content], f"{players_dict[rep1.content].mention}, you and {players_dict[rep2.content].mention} are the lovers!")
            await client.send_message(players_dict[rep2.content], f"{players_dict[rep2.content].mention}, you and {players_dict[rep1.content].mention} are the lovers!")

            holder[roles_dict['cupid']].call_pass = False
    
    #GUARDIAN - call
    if 'guardian' in list(roles_dict.keys()):
        box_guardian = await msg_embe("**Guard! Gear up and do your job!**", 0xFAFAFA)
        await client.say(embed=box_guardian)
        if holder[roles_dict['guardian']].status and holder[roles_dict['guardian']].role == 'guardian':    
            await client.send_message(players_dict[roles_dict['guardian']], "So who'd you like to protect? If you don't, please use `none`.")
            rep = await client.wait_for_message(author=players_dict[roles_dict['guardian']])
            while rep.content not in players_list or rep.content == prevsavi:
                if rep.content == 'none': break
                if rep.content == prevsavi:
                    await client.say(":o: Bạn không thể bảo vệ cùng một người trong 2 đêm liên tiếp!")
                    rep = await client.wait_for_message(author=players_dict[roles_dict['guardian']])
                    continue
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['guardian']], ":o: Xin hãy chọn người **còn sống**!")
                        rep = await client.wait_for_message(author=players_dict[roles_dict['guardian']])
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['guardian']], ":o: I don't know that guy, is he **in the game**?!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['guardian']])
            if rep.content != 'none' and rep.content not in save_wish:
                save_wish.append(rep.content)
                prevsavi = rep.content
            #Message to the GM (if available)
            if GM != 'Cli':
                tm = ''
                tm = strftime("%H:%M:%S", gmtime())
                await client.send_message(GM_dict['GM'], f"`{tm}`\t:shield: |\t **{holder[roles_dict['guardian']].name}** (as *Guardian*) has protected **{rep.content}**.")
            await client.send_message(players_dict[roles_dict['guardian']], ":ok_hand:")
        else:
            sleep(5)

    #WOLF - call
    box_wolf = await msg_embe("**Wolves! You're hungry? There's always hooman waiting for you.. to be chewed, ofc!**", 0xFF3600)
    await client.say(embed=box_wolf)
    try:
        death = await bite(holder)
        if death != 'none':
            death_bywolf_wish.append(death)
    except:
        print("ERROR AT WOLF - call.")
        pass

    #TREE - call
    if 'tree' in list(roles_dict.keys()):
        box_tree = await msg_embe("**Tree-san tree-san, who would you want to tree on?**", 0x2886B9)
        await client.say(embed=box_tree)
        await tree(holder)

    #WITCH - call
    if 'witch' in list(roles_dict.keys()):
        #HEALING
        box_witch1 = await msg_embe("**Dear witchy, there's still one healing pod on your shelf. Wanna get rid of karma?**", 0xC09DF3)
        box_witch2 = await msg_embe("**P/s: Karma sucks. Go kill someone with your devious poison fluid ( ͡° ͜ʖ ͡°)**", 0xC09DF3)
        await client.say(embed=box_witch1)
        if holder[roles_dict['witch']].status == True and holder[roles_dict['witch']].heal_pod == 1 and holder[roles_dict['witch']].role == 'witch':
            await client.send_message(players_dict[roles_dict['witch']], "Choose someone you want to save. `none` to omit.")
            rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            while rep.content not in players_list:
                if rep.content == 'none': break
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['witch']], ":o: Even lolies can't save a *dead* man you know...")
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['witch']], ":o: I don't know that guy, is he **in the game**?!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            if rep.content != 'none':
                save_wish.append(rep.content)
                holder[roles_dict['witch']].heal_pod = 0
            else:
                pass
            #Message to the GM (if available)
            if GM != 'Cli':
                tm = ''
                tm = strftime("%H:%M:%S", gmtime())
                await client.send_message(GM_dict['GM'], f"`{tm}`\t:pill: |\t **{holder[roles_dict['witch']].name}** (as *Witch*) has used healing on **{rep.content}**.")
            await client.send_message(players_dict[roles_dict['witch']], ":ok_hand:")
        else:
            sleep(10)
        #POISONING
        await client.say(embed=box_witch2)
        if holder[roles_dict['witch']].status == True and holder[roles_dict['witch']].kill_pod == 1 and holder[roles_dict['witch']].role == 'witch':
            await client.send_message(players_dict[roles_dict['witch']], "Choose someone you want to kill, `none` to omit.")
            rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            while rep.content not in players_list:
                if rep.content == 'none': break
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['witch']], ":o: Even dildos can't choke a dead body til death you know...")
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['witch']], ":o: I don't know that guy, is he **in the game**?!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            if rep.content != 'none':
                death_byman_wish.append(rep.content)
                holder[roles_dict['witch']].kill_pod = 0
            else:
                pass
            #Message to the GM (if available)
            if GM != 'Cli':
                tm = ''
                tm = strftime("%H:%M:%S", gmtime())
                await client.send_message(GM_dict['GM'], f"`{tm}`\t:skull_crossbones: |\t **{holder[roles_dict['witch']].name}** (as *Witch*) has used poison pot on **{rep.content}**.")
            await client.send_message(players_dict[roles_dict['witch']], ":ok_hand:")
        else:
            sleep(10)

    #ELDER - call
    if 'elder' in list(roles_dict.keys()):
        if holder[roles_dict['elder']].call_pass:
            box_elder = msg_embe("**Grandny wake up! Here's some sleeping pills**", 0x858585)
            await client.say(embed=box_elder)
            await client.send_message(players_dict[roles_dict['elder']], "Go to sleep :>")
            holder[roles_dict['elder']].call_pass = False

    #HUNTER - call
    if 'hunter' in list(roles_dict.keys()):
        box_hunter = await msg_embe("**Hunter. Huntress. May the odds be ever in your favor!**", 0xEE9C3A)
        await client.say(embed=box_hunter)
        await client.send_message(players_dict[roles_dict['hunter']], "Aim someone. Anyone.")
        if holder[roles_dict['hunter']].status == True and holder[roles_dict['hunter']].role == 'hunter':
            rep = await client.wait_for_message(author=players_dict[roles_dict['hunter']])
            while rep.content not in players_list:
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['hunter']], ":o: Xin hãy chọn người **còn sống**!")
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['hunter']], ":o: I mean not that one, is he even **in the game**?!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['hunter']])
            holder[roles_dict['hunter']].prey = rep.content
            #Message to the GM (if available)
            if GM != 'Cli':
                tm = ''
                tm = strftime("%H:%M:%S", gmtime())
                await client.send_message(GM_dict['GM'], f"`{tm}`\t:gun: |\t **{holder[roles_dict['hunter']].name}** (as *Hunter*) aimed his gun at **{rep.content}**.")
            await client.send_message(players_dict[roles_dict['hunter']], ":ok_hand:")
        else:
            sleep(7)

    if GM == 'Cli':
        death_list = await sentence(holder, death_byman_wish, death_bywolf_wish, death_byGM_wish, save_wish)
        await phase_inform(holder, 'night', death_list)
    else:
        await client.send_message(GM_dict['GM'], f':bulb: Use `..botkill` to let bot automatically kill, `..kill [p1] [p2] [..]` to do it manually.')
        rr = True
        while rr == True:    
            inp1 = await client.wait_for_message(author=GM_dict['GM'])
            raw1 = word_tokenize(inp1.content)
            if raw1[0] == '..botkill':
                death_list = await sentence(holder, death_byman_wish, death_bywolf_wish, death_byGM_wish, save_wish)
                await phase_inform(holder, 'night', death_list)
                #Check if all the players are dead. If true, lock = False. This one's only in GM-mode
                for i in players_list:
                    lock = False
                    if holder[i].status == True: lock = True; break
                return          
            elif raw1[0] == '..kill':
                for p in raw1[1:]:
                    if p not in players_list or holder[p].status == False: await client.send_message(GM_dict['GM'], f":warning: Whether **{p}**'s ded, whether **{p}**'s not even in the game :<"); break
                    else: death_byGM_wish.append(p); rr = False; break
                #Check if all the players are dead. If true, lock = False. This one's only in GM-mode
                for i in players_list:
                    lock = False
                    if holder[i].status == True: lock = True; break
        death_list = await sentence(holder, death_byman_wish, death_bywolf_wish, death_byGM_wish, save_wish)  
        await phase_inform(holder, 'night', death_list)

async def day(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global vote_dict
    global db_time
    global GM_dict
    global GM
    global lock
    vote_dict.clear()
    max_vote_player = []
    
    death_bywolf_wish = []
    death_byman_wish = []
    death_byGM_wish = []
    death_list = []
    save_wish = []

    if GM != 'Cli':
        await client.send_message(GM_dict['GM'], f":page_facing_up: **Moring - DAY {DAY}**")
    await client.say(f"============ HENCE ROSE THE DAWN :white_sun_small_cloud: DAY {DAY} BEGUN! ============")
    if GM == 'Cli':
        await loop_check(holder)
        max_vote_player = await vote_check(holder)
        await client.say(f":stopwatch: **{' and '.join(max_vote_player)}**, you have `{db_time} secs` to defend yourself! \n:warning: You still can change your vote simply by voting the one you want.")    
        await loop_timer()
        max_vote_player = await vote_check(holder)
        #Check max_vote_player
        if len(max_vote_player) == 1:
            death_byman_wish.append(max_vote_player[0])
            await client.say(f":skull: ** URGHH ** :skull: {max_vote_player[0]} has learnt to float...")
    
        death_list = await sentence(holder, death_byman_wish,  death_bywolf_wish, death_byGM_wish, save_wish)

        await phase_inform(holder, 'day', death_list)
    else:
        await loop_check(holder)
        max_vote_player = await vote_check(holder)
        await client.say(f":bulb: Players still can revote if they change their mind, simply by vote the one you want\n:bulb: GM {GM_dict['GM'].mention}, use `..count` to save the votes, use `..next` to save the votes *and* move the next phase.")
        while True:
            inp = await client.wait_for_message(author=GM_dict['GM'])
            if inp.content == '..next':
                max_vote_player = await vote_check(holder)
                #Check max_vote_player
                if len(max_vote_player) == 1:
                    death_byman_wish.append(max_vote_player[0])
                    await client.say(f":skull: ** URGHH ** :skull: {max_vote_player[0]} has learnt to float...")
    
                death_list = await sentence(holder, death_byman_wish,  death_bywolf_wish, death_byGM_wish, save_wish)

                await phase_inform(holder, 'day', death_list)
                #Check if all the players are dead. If true, lock = False. This one's only in GM-mode
                for i in players_list:
                    lock = False
                    if holder[i].status == True: lock = True; break
                break
            elif inp.content == '..count':
                max_vote_player = await vote_check(holder)


@client.command()
async def ping():
    await client.say("```PING \nPONG```")



async def vote_check(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global vote_dict
    global vote_board

    keys = []
    board = ''
    max_vote_player = []         #A list contains name(s) of whose votes for them highest
    pvotes_dict = {}             #A dict consists of players and their votes for them
    votes = list(vote_dict.values())

    #Go through names in players_list, check if it's alive. If true, add its name and its votes for it to pvotes_dict
    for name in players_list:
        if holder[name].status == True:
            pvotes_dict[name] = votes.count(name)

    keys = list(pvotes_dict.keys())
    try:
        max_vote = max(list(pvotes_dict.values()))           #Highest num of vote along pvotes_dict values
    except ValueError:
        max_vote = 'n/a'
    #Go through names in players_list, check if it's alive and its votes equal to max_vote. If true, add its name to max_vote_player
    for name in players_list:
        if holder[name].status == True and pvotes_dict[name] == max_vote:
            max_vote_player.append(name)
    
    #Generate votes board msg
    for i in keys:
        if keys.index(i) == 0 and len(keys) > 1:
            board = f'```{i}    ------------    {pvotes_dict[i]} vote(s)'
        elif keys.index(i) == int(len(keys) - 1):
            if len(keys) > 1:
                seq = (board, f" \n{i}    ------------    {pvotes_dict[i]} vote(s)```")
                board = ''.join(seq)
            else:
                board = f"```{i}    ------------    {pvotes_dict[i]} vote(s)```"
        else:
            seq = (board, f" \n{i}    ------------    {pvotes_dict[i]} vote(s)")
            board = ''.join(seq)

    #Send board msg, and top vote
    vote_board = str(board)
    await client.say(board)
    await client.say(f"```autohotkey\nThe most hated man: {' || '.join(max_vote_player)}```")

    return max_vote_player




async def loop_check(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global vote_dict
    alive = []

    for p in players_list:
        if holder[p].status:
            alive.append(p)
    
    while True:
        print("------------------HERE-------------------")
        print(f"{len(list(vote_dict))} {len(alive)}")
        if len(list(vote_dict)) == len(alive):
            break
        await asyncio.sleep(5)

async def loop_timer():
    global db_time    
    db_time = 30

    while True:
        await asyncio.sleep(1)
        db_time -= 1
        if db_time == 0: break
        if db_time == 15: await client.say(f":stopwatch: Defending time ends in `{db_time}`!")
        elif db_time == 5: await client.say(f":stopwatch: Defending time ends in `{db_time}`!")
        elif db_time < 5: await client.say(f":stopwatch: `{db_time}`")

    #Reset the value
    db_time = 30

async def sentence(holder, death_byman_wish, death_bywolf_wish, death_byGM_wish, save_wish):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    death_list = []

    #Scan and sentence players in death_byman_wish, init the effect of particular roles.
    if death_byman_wish:
        for p in death_byman_wish:
            if p in save_wish:
                continue
            holder[p].lives -= 1
            if holder[p].prey:
                holder[holder[p].prey].lives -= 1
            if holder[p].lover:
                holder[holder[p].lover].lives -= 1
            if holder[p].role == 'elder':
                elder_ban(holder)
                holder[p].lives -= 1

    #Scan and sentence players in death_bywolf_wish, init the effect of particular roles.
    if death_bywolf_wish:
        for p in death_bywolf_wish:
            if p in save_wish:
                continue
            holder[p].lives -= 1
            if holder[p].prey:
                holder[holder[p].prey].lives -= 1
            if holder[p].lover:
                holder[holder[p].lover].lives -= 1

    #Scan and sentence players in death_byGM_wish.
    if death_byGM_wish:
        for p in death_byGM_wish:
            if holder[p].role == 'elder':
                elder_ban(holder)
                holder[p].lives -= 1
                await client.send_message(GM_dict['GM'], f":warning: {p}, as **elder**, is dead, other special roles' abilities are removed! GM should check `-stt` for better updates.")
            else: holder[p].lives -= 1

    #Take action.
    for p in players_list:
        if holder[p].lives < 1 and holder[p].status == True:
            holder[p].status = False
            death_list.append(holder[p].name)
    
    return death_list

async def judge(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global lock
    wolf = 0; villagers = 0; lovers = 0

    #Identify roles member
    for p in players_list:
        if holder[p].status == False: continue
        if holder[p].role == 'wolf':
            wolf += 1
        else:
            villagers += 1
        if holder[p].lover:
            if holder[p].role == 'wolf' and holder[holder[p].lover].role != 'wolf' or holder[p].role != 'wolf' and holder[holder[p].lover].role == 'wolf':
                lovers += 1
            
    print(f"wolf({wolf}) --- villagers({villagers}) --- lovers({lovers})")

    #Measuring
    if wolf == 0 and villagers == 0 and lovers == 0: 
        await client.say("---------------------------------------------- \n\t\t\t\t\t\t**DRAW!**\n----------------------------------------------")
        lock = False
        return
    if wolf >= villagers:
        if wolf > villagers:
            await client.say("---------------------------------------------- \n\t\t\t:wolf: **WOLVES** WON! :wolf:\n----------------------------------------------")
            lock = False
        elif wolf == villagers:
            if int(wolf + villagers) == 4 and lovers == 2 or int(wolf + villagers) == 3 and lovers == 2 or lovers == int(wolf + villagers):         #2or3or4players
                await client.say("---------------------------------------------- \n\t\t\t:couple_mm: **LOVERS WON!** :couple_ww:\n----------------------------------------------")
                lock = False
            else:                                   #nplayers
                await client.say("---------------------------------------------- \n\t\t\t:wolf: **WOLVES** WON! :wolf:\n----------------------------------------------")
                lock = False    
    elif wolf < villagers:
        if int(wolf + villagers) == 4 and lovers == 2:
            await client.say("---------------------------------------------- \n\t\t\t:couple_mm: **LOVERS WON!** :couple_ww:\n----------------------------------------------")
            lock = False
        elif wolf == 0:
            await client.say("---------------------------------------------- \n\t\t\t:cowboy: **VILLAGERS WON!** :cowboy:\n----------------------------------------------")
            lock = False

async def phase_inform(holder, phase, death_list):
    global players_list
    global players_dict
    global roles_list
    global roles_dict

    #Update the status_dict
    await status_update(holder)

    if phase == 'night':
        await client.say("Last night we had...")
        await asyncio.sleep(random.choice([2, 3]))
        await client.say(f".. {len(death_list)} people ded!")
        if len(death_list) != 0:    
            for i in death_list:
                await asyncio.sleep(random.choice([1, 2, 3]))
                await client.say(f"{players_dict[i].mention} is deadsu yo~")
        else:
            await client.say("Sigh in relief :>")
    elif phase == 'day':
        await client.say("And so it was...")
        await client.say("......")
        await asyncio.sleep(0.5)
        if len(death_list) != 0:    
            for i in death_list:
                await asyncio.sleep(random.choice([1, 2, 3]))
                await client.say(f"... {players_dict[i].mention} that left this world...")
        else:
            await client.say("... noone. NOONE'S HANG! *REEEEEEEEEE* :>")


async def elder_ban(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict

    for i in players_list:
        if holder[i].status == True and holder[i].role in ['witch', 'guardian', 'tree']:
            holder[i].role = 'villager'

async def tree(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict

    await client.send_message(players_dict[roles_dict['tree']], "Choose some one you want to treeeeeeeeeeeeeeeeeeee!")
    if holder[roles_dict['tree']].status and holder[roles_dict['tree']].role == 'tree':
        rep = await client.wait_for_message(author=players_dict[roles_dict['tree']])
        while rep.content not in players_list:
            try:
                if not holder[rep.content].status:
                    await client.send_message(players_dict[roles_dict['tree']], ":o: Xin hãy chọn người **còn sống**!")
                    continue
            except: pass
            await client.send_message(players_dict[roles_dict['tree']], ":o: I don't know that guy, is he **in the game**?!")
            rep = await client.wait_for_message(author=players_dict[roles_dict['tree']])
        if holder[rep.content].role == 'wolf':
            await client.send_message(players_dict[roles_dict['tree']], f"{players_dict[roles_dict['tree']].mention}, **nod nod nod**")
        else:
            await client.send_message(players_dict[roles_dict['tree']], f"{players_dict[roles_dict['tree']].mention}, **shake shake shake**")
        #Message to the GM (if available)
        if GM != 'Cli':
            tm = ''
            tm = strftime("%H:%M:%S", gmtime())
            await client.send_message(GM_dict['GM'], f"`{tm}`\t:black_joker: |\t **{holder[roles_dict['tree']].name}** (as a *Tree*) has treed on **{rep.content}**.")
    else:
        sleep(8)

async def bite(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    reps = []
    death = ''

    while len(list(set(reps))) != 1:
        for i in roles_dict['wolf']:
            if holder[i].status == True  and holder[i].role == 'wolf':
                await client.send_message(players_dict[i], "Choose someone you wanna bite, `none` to omit. Remember that all wolves have to choose the same prey, or you'll have to pick a again.")
                rep = await client.wait_for_message(author=players_dict[i])
                while rep.content not in players_list:
                    if rep.content == 'none': break
                    try:
                        if not holder[rep.content].status:
                            await client.send_message(players_dict[i], ":o: Xin hãy chọn người **còn sống**!")
                            continue
                    except: pass
                    await client.send_message(players_dict[i], ":o: I don't know that guy, is he **in the game**?!")
                    rep = await client.wait_for_message(author=players_dict[i])   
                for a in roles_dict['wolf']:
                    if rep.content == 'none':
                        await client.send_message(players_dict[a], f"{players_dict[i].mention} didn't chose anyone!")
                    else:
                        await client.send_message(players_dict[a], f"{players_dict[i].mention} wants to bite {rep.content}")
                reps.append(rep.content)
            else:
                sleep(7)

    if rep.content != 'none':
        death = rep.content
    else: death = 'none'
    #Message to the GM (if available)
    if GM != 'Cli':
        tm = ''
        tm = strftime("%H:%M:%S", gmtime())
        await client.send_message(GM_dict['GM'], f"`{tm}`\t:wolf: |\t **{holder[roles_dict['wolf']].name}** (as *Wolf*) bited **{rep.content}**.")
    print(death)
    try:
        return death
    except:
        pass


async def status_update(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global status_dict
    static = ''
    
    status_dict.clear()
    #Run through the players_list
    for p in players_list:
        if holder[p].status: static = 'ALIVE'
        else: static = 'DEAD'
    
        #Update the status dict
        status_dict[holder[p].name] = static

async def game_stt_check():
    global roles_dict
    stt = ''

    if list(roles_dict.keys()): stt = 'on'; return stt
    elif not list(roles_dict.keys()): stt = 'off'; return stt

async def data_clear_procedure():
    global players_list
    global players_dict
    global roles_dict
    global GM
    global GM_dict

    players_list.clear()
    players_dict.clear()
    roles_dict.clear()
    GM = 'Cli'
    GM_dict.clear()

async def msg_embe(msg, clc):
    embed_msg = discord.Embed(
        title = msg,
        colour = discord.Colour(clc)
    )
    return embed_msg

async def setup_get():
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global channel_bind
    global CONS_roles_list
    global GM
    global GM_dict
    chnl = ''; mode = ''; stt = ''; plists = []; roles = ''

    #Joined players
    if players_list: 
        for p in players_list:
            plists.append(players_dict[p].mention)
    else:
        plists = ['n/a']

    #Roles
    roles = '` `'.join(CONS_roles_list)

    #Get the game status
    mode = await game_stt_check()
    if mode == 'on': stt = "Game has already started! \n**______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______**"
    else: stt = "Game has **NOT** started yet. \n**______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______**"

    #Get the chnl
    if channel_bind: chnl = channel_bind
    else: chnl = 'you\'re standing at'

    box_setup = discord.Embed(
        title = f"Setting up for #{chnl}",
        description = stt,
        colour = discord.Colour(0x011C3A)
    )
    box_setup.add_field(name=f'Joined ({int(len(players_list))})', value=', '.join(plists), inline=True)
    if GM == 'Cli':    
        box_setup.add_field(name=f'Game Master', value=GM, inline=True)
    else: box_setup.add_field(name=f'Game Master', value=GM_dict['GM'].mention, inline=True)
    box_setup.add_field(name=f'Cards ({len(CONS_roles_list)})', value=f"`{roles}`", inline=False)
    
    await client.say(embed=box_setup)

async def reveal(holder):
    global players_list
    global players_dict
    global roles_dict
    reveal_board = ''
    sign = ''

    for i in players_list:
        if holder[i].lover: sign = ':couple_with_heart:'
        else: sign = ' '
        reveal_board = reveal_board + " \n| " + f"{players_dict[i].mention} is {holder[i].role} {sign}"
    
    await client.say(reveal_board)

def help_dict_plugin():
    global help_dict
    d = ''
    raw = []

    with open("help_dict.txt", 'r', encoding='utf-8-sig') as f:
        for line in f:
            d = line
            raw = word_tokenize(d)
            try:
                help_dict[str(' '.join(raw[:int(raw.index('='))]))] = str(' '.join(raw[int(raw.index('=') + 1):]))
            except:
                continue

os.getenv('TOKEN')
client.run(TOKEN) 
