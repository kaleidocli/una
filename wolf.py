import discord
from discord.ext import commands

from time import sleep
from os import listdir
import os
import random
import asyncio
import threading
from nltk import word_tokenize 

channel_bind = ''
help_dict = {}

#holder = {}
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

TOKEN = 'NDQ5Mjc4ODExMzY5MTExNTUz.DeiXGg.4qhnjnBG8EGpUxEorp1h8wYxLVk'

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
        box.add_field(name='Werewolf', value='`help` `cast` `assign` `resign` `setcard` `start` `vote` `stt` `addtime`', inline=False)
        box.add_field(name='Config', value="""`bind` `unbind`""", inline=False)
        box.add_field(name="Rules, Functions and FAQ about the game", value="[Default](http://luatmasoi.blogspot.com/2017/05/huong-dan-luat-ma-soi-viet-hoa-mo-rong.html) || [One-Night](http://thegioiboardgame.vn/blogs/board-game-nhap-mon/1000049261-huong-dan-choi-bai-ma-soi-one-night)")
        box.set_footer(text="use `-help <command>` for more info about the command.")
        await client.say(embed=box)
    elif help_key in list(help_dict.keys()):
        box_small = discord.Embed(
            title = f'**-{help_key}**',
            description = f"{help_dict[help_key]}",
            colour = discord.Colour(0x011C3A)
        )
        await client.say(embed=box_small)
    else:
        await client.say(":warning: Please only use one of the available commands.")

    

@client.command(pass_context=True)
async def bind(ctx):
    global channel_bind
    if not channel_bind:
        channel_bind = ctx.message.channel.name
        await client.say(f":white_check_mark: Binded to channel {ctx.message.channel.name}!")
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
        await client.say(":upside_down: Game mở rồi đó cha nội!")
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
        await client.say(f":upside_down: Đóng gì đóng hoài vậy {ctx.message.author.name}...")
        return

    #Check if game has started yet
    mode = await game_stt_check()
    if mode == 'on': await client.say(f"Người ta đang chơi mà đòi phá game hở {ctx.message.author.mention} =))"); return

    lock = False
    db_time = 30
    PHASE = 'n/a'
    slots = 0
    await data_clear_procedure()
    channel_bind = ''
    box = await msg_embe(':tada: **Avada kedavra!** The game is *gone*, oof.', 0x011C3A)
    await client.say(embed=box)

@client.command(pass_context=True)
async def assign(ctx):
    global players_list
    global players_dict
    global slots
    clc = 0; mode = ''

    #Check if game has started yet
    mode = await game_stt_check()
    if mode == 'on': await client.say(f"{ctx.message.author.mention} chậm chân rồi :< Game còn dang dở nên thôi ngồi chờ đỡ nha {ctx.message.author.name}."); return

    #Check if game's opened or there are any slots left
    if not roles_list:  await client.say(f":x: Hình như chưa có game nào bắt đầu, hoặc là có mà game hết slots rồi á, {ctx.message.author.name}. Sumimasen!"); return
    if ctx.message.author.name not in players_list:
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
    global slots
    clc = 0

    #Check if game's opened or there are any slots left
    if not roles_list:  await client.say(f":x: {ctx.message.author.name} đã `-assign` đâu mà đòi `-resign` :>"); return
    if ctx.message.author.name in players_list:
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
            await client.say(f":raised_hand: {ctx.message.author.mention} đã vote cho {players_dict[raw[0]].mention} lên giàn! --- [{len(list(vote_dict.keys()))}/{len(alive)} số người đã vote]")       
        else:
            await client.say(f"{ctx.message.author.mention}, please vote a player **in the list** that is **still alive**.")
    except IndexError:
        await client.say(vote_board)

@client.command(pass_context=True)
async def setcard(ctx, *args):
    global roles_list
    global STNDRD_roles_list
    global CONS_roles_list
    global lock
    stt = ''; cards = []

    if not lock: await client.say(":warning: **Hiện tại chưa có game nào nha!** Cần thì dùng `-create` để tạo game."); return
    stt = await game_stt_check()
    if stt == 'on': await client.say(":warning: Ê ê ai cho đổi card **giữa trận** thế!"); return

    for card in args:
        if card in STNDRD_roles_list:
            cards.append(card)
        else: 
            await client.say(f":x: `{card}` card not available!")
            return
    roles_list = cards.copy()
    CONS_roles_list = roles_list.copy()
    await setup_get()

@client.command(pass_context=True, aliases=['+t'])
async def addtime(ctx, *args):
    global db_time
    global PHASE
    sample = 0
    raw = []

    #Check if the current phase is DAY
    if PHASE != 'day': await client.say(":warning: Ban ngày mới sử dụng lệnh này được :< Mà game bắt đầu chưa thế?"); return

    sample = int(db_time)
    for t in args:
        try:
            int(t)
        except ValueError:
            await client.say(":warning: Đưa tui *integer* thôi, tui ngu lắm >.<")
            return
        raw.append(t)
    sample += int(raw[0])
    if sample > 300:
        await client.say(":warning: Cho tán nhảm tầm **5 mins** (300 secs) thôi! Hông đòi thêm được nữa đâu, hiểu không!?")
        return
    else:
        db_time += int(raw[0])
        await client.say(f":white_check_mark: Now you have `{db_time}` secs left to watch your friends suffer <3")

@client.command()
async def stt():
    global status_dict
    global players_dict
    global lock
    keys = list(status_dict.keys())
    static =  ''
    board = ''

    #Check if there's a game
    if not bool(players_dict): await client.say(":x: Có game đâu mà đòi status =))"); return
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



@client.command()
async def start():
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global PHASE
    global DAY
    wolf = []; villager = []

    #Check if there's enough players
    if len(players_list) < 1: 
        await client.say("Not enough players!")
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

    #Inform role for each player
    for name in players_list:    
        await client.send_message(players_dict[name], f"Your role: << {holder[name].role} >>")
    #Message names of other wolves for each wolf
    for name in wolf:
        rest = wolf.copy(); rest.remove(name)
        await client.send_message(players_dict[name], f":wolf: You, {' and '.join(rest)} are wolves. Have a good hunt! :wolf: ")

    print(roles_list)
    print(roles_dict)
    print(players_dict)
    while lock:
        DAY += 1
        #Update status_dict
        await status_update(holder)
        
    # NIGHT PHASE
        PHASE = 'night'
        await night(holder)
        try:    
            await judge(holder)
        except: pass
        if not lock: break
        #Update status_dict
        status_update(holder)
    # DAY PHASE        
        PHASE = 'day'
        await day(holder)
        try:
            await judge(holder)
        except: pass
        if not lock: break
    await reveal(holder)
    await data_clear_procedure()
    


async def night(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global prevsavi

    death_bywolf_wish = []
    death_byman_wish = []
    death_list = []
    save_wish = []

    await client.say("===========:waxing_gibbous_moon:=== MÀN ĐÊM DẦN BUÔNG XUỐNG ===:waxing_gibbous_moon:============")

    #CUPID - call
    if 'cupid' in list(roles_dict.keys()):
        if holder[roles_dict['cupid']].call_pass:
            box_cupid = await msg_embe("**Cupid ơi dậy đi nào!!!!**", 0xFED0EE)
            await client.say(embed=box_cupid)
        
            await client.send_message(players_dict[roles_dict['cupid']], "Hãy chọn người bạn muốn bắn")
            rep1 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])
            while rep1.content not in players_list:
                await client.send_message(players_dict[roles_dict['cupid']], "Xin hãy chọn người ở trong list!")
                rep1 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])

            await client.send_message(players_dict[roles_dict['cupid']], "Hãy chọn người tiếp theo bạn muốn bắn")
            rep2 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])
            while rep2.content not in players_list:
                await client.send_message(players_dict[roles_dict['cupid']], "Xin hãy chọn người ở trong list!")
                rep2 = await client.wait_for_message(author=players_dict[roles_dict['cupid']])

            holder[rep1.content].lover = rep2.content
            holder[rep2.content].lover = rep1.content
            client.send_message(players_dict[rep1.content], f"{players_dict[rep1.content].mention}, you and {players_dict[rep2.content].mention} are the lovers!")
            await client.send_message(players_dict[rep2.content], f"{players_dict[rep2.content].mention}, you and {players_dict[rep1.content].mention} are the lovers!")

            holder[roles_dict['cupid']].call_pass = False
    
    #GUARDIAN - call
    if 'guardian' in list(roles_dict.keys()):
        box_guardian = await msg_embe("**Bảo vệ ơiii dậy đi nào! Bảo vệ muốn bảo vệ ai nào?**", 0xFAFAFA)
        await client.say(embed=box_guardian)
        if holder[roles_dict['guardian']].status and holder[roles_dict['guardian']].role == 'guardian':    
            await client.send_message(players_dict[roles_dict['guardian']], "Xin hãy chọn người bạn muốn bảo vệ. Nếu không, hãy nhập 'none'.")
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
                await client.send_message(players_dict[roles_dict['guardian']], ":o: Xin hãy chọn người ở trong list!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['guardian']])
            if rep.content != 'none' and rep.content not in save_wish:
                save_wish.append(rep.content)
                prevsavi = rep.content
            await client.send_message(players_dict[roles_dict['guardian']], ":ok_hand:")
        else:
            sleep(5)

    #WOLF - call
    box_wolf = await msg_embe("**Sói ơiii dậy đi nào! Sói muốn đợp ai nào?**", 0xFF3600)
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
        box_tree = await msg_embe("**Tiên tri ơiii dậy nào! Tree muốn tree ai nào?**", 0x2886B9)
        await client.say(embed=box_tree)
        await tree(holder)

    #WITCH - call
    if 'witch' in list(roles_dict.keys()):
        #HEALING
        box_witch1 = await msg_embe("**Phù thủy ơiii dậy cái nào!! Thủy muốn dùng bình cứu lên ai nào?**", 0xC09DF3)
        box_witch2 = await msg_embe("**Phù thủy ơiii dậy cái nào!! Thủy muốn dùng bình độc lên ai nào?**", 0xC09DF3)
        await client.say(embed=box_witch1)
        if holder[roles_dict['witch']].status == True and holder[roles_dict['witch']].heal_pod == 1 and holder[roles_dict['witch']].role == 'witch':
            await client.send_message(players_dict[roles_dict['witch']], "Hãy chọn người bạn muốn **cứu**, chọn 'none' để không làm gì.")
            rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            while rep.content not in players_list:
                if rep.content == 'none': break
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['witch']], ":o: Xin hãy chọn người **còn sống**!")
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['witch']], ":o: Xin hãy chọn người ở trong list!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            if rep.content != 'none':
                save_wish.append(rep.content)
                holder[roles_dict['witch']].heal_pod = 0
            else:
                pass
            await client.send_message(players_dict[roles_dict['witch']], ":ok_hand:")
        else:
            sleep(10)
        #POISONING
        await client.say(embed=box_witch2)
        if holder[roles_dict['witch']].status == True and holder[roles_dict['witch']].kill_pod == 1 and holder[roles_dict['witch']].role == 'witch':
            await client.send_message(players_dict[roles_dict['witch']], "Hãy chọn người bạn muốn **giết**, chọn 'none' để không làm gì.")
            rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            while rep.content not in players_list:
                if rep.content == 'none': break
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['witch']], ":o: Xin hãy chọn người **còn sống**!")
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['witch']], ":o: Xin hãy chọn người ở trong list!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['witch']])
            if rep.content != 'none':
                death_byman_wish.append(rep.content)
                holder[roles_dict['witch']].kill_pod = 0
            else:
                pass
            await client.send_message(players_dict[roles_dict['witch']], ":ok_hand:")
        else:
            sleep(10)

    #ELDER - call
    if 'elder' in list(roles_dict.keys()):
        if holder[roles_dict['elder']].call_pass:
            box_elder = msg_embe("**Già làng ơi dậy đi ngủ nào!!**", 0x858585)
            await client.say(embed=box_elder)
            await client.send_message(players_dict[roles_dict['elder']], "Đi ngủ đi :>")
            holder[roles_dict['elder']].call_pass = 0

    #HUNTER - call
    if 'hunter' in list(roles_dict.keys()):
        box_hunter = await msg_embe("**Thợ săn ơi dậy đi nàooooooo!**", 0xEE9C3A)
        await client.say(embed=box_hunter)
        await client.send_message(players_dict[roles_dict['hunter']], "Hãy chọn người bạn muốn nhắm!")
        if holder[roles_dict['hunter']].status == True and holder[roles_dict['hunter']].role == 'hunter':
            rep = await client.wait_for_message(author=players_dict[roles_dict['hunter']])
            while rep.content not in players_list:
                try:
                    if not holder[rep.content].status:
                        await client.send_message(players_dict[roles_dict['hunter']], ":o: Xin hãy chọn người **còn sống**!")
                        continue
                except: pass
                await client.send_message(players_dict[roles_dict['hunter']], ":o: Xin hãy chọn người ở trong list!")
                rep = await client.wait_for_message(author=players_dict[roles_dict['hunter']])
            holder[roles_dict['hunter']].prey = rep.content
            await client.send_message(players_dict[roles_dict['hunter']], ":ok_hand:")
        else:
            sleep(7)

    death_list = await sentence(holder, death_byman_wish, death_bywolf_wish, save_wish)
    
    await phase_inform(holder, 'night', death_list)

async def day(holder):
    global players_list
    global players_dict
    global roles_list
    global roles_dict
    global vote_dict
    global db_time
    vote_dict.clear()
    max_vote_player = []
    
    death_bywolf_wish = []
    death_byman_wish = []
    death_list = []
    save_wish = []

    await client.say(f"============ BÌNH MINH LÓ DẠNG :white_sun_small_cloud: NGÀY {DAY} BẮT ĐẦU! ============\n:bulb: NOTE: Kiếm một thằng mà treo cổ đi :>")
    await loop_check(holder)
    max_vote_player = await vote_check(holder)
    await client.say(f":stopwatch: **{' và '.join(max_vote_player)}**, bạn có `{db_time} giây` để biện luận! \n:warning: Các bạn vẫn có thể đổi vote của mình bằng cách vote người mình muốn vote.")    
    await loop_timer()
    max_vote_player = await vote_check(holder)

    #Check max_vote_player
    if len(max_vote_player) == 1:
        death_byman_wish.append(max_vote_player[0])
        await client.say(f":skull: ** PHỰC ** :skull: Tiếng thòng lòng quanh cổ {max_vote_player[0]} nặng nề vang lên...")
    
    death_list = await sentence(holder, death_byman_wish, death_bywolf_wish, save_wish)

    await phase_inform(holder, 'day', death_list)

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
    await client.say(f"```autohotkey\nThòng lọng ngay trước cổ: {' || '.join(max_vote_player)}```")

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
        if db_time == 15: await client.say(f":stopwatch: Thời gian bào chữa còn `{db_time}`!")
        elif db_time == 5: await client.say(f":stopwatch: Thời gian bào chữa còn `{db_time}`!")
        elif db_time < 5: await client.say(f":stopwatch: `{db_time}`")

    #Reset the value
    db_time = 30

async def sentence(holder, death_byman_wish, death_bywolf_wish, save_wish):
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
        if holder[p].lover != None:
            if holder[p].role == 'wolf' and holder[holder[p].lover].role != 'wolf' or holder[p].role != 'wolf' and holder[holder[p].lover].role == 'wolf':
                lovers += 1
            
        

    #Measuring
    if wolf == 0 and villagers == 0 and lovers == 0: 
        await client.say("---------------------------------------------- \n\t\t\t\t\t\t**DRAW!**\n----------------------------------------------")
        lock = False
        return
    if wolf >= villagers:
        if lovers != 2:
            await client.say("---------------------------------------------- \n\t\t\t:wolf: **WOLVES** WON! :wolf:\n----------------------------------------------")
            lock = False
        else:
            if lovers == int(wolf + villagers):
                await client.say("---------------------------------------------- \n\t\t\t:couple_mm: **LOVERS WON!** :couple_ww:\n----------------------------------------------")
                lock = False
            else: pass
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
        await client.say("Tối qua chúng ta có...")
        await asyncio.sleep(random.choice([2, 3]))
        await client.say(f".. {len(death_list)} người chết!")
        if len(death_list) != 0:    
            for i in death_list:
                await asyncio.sleep(random.choice([1, 2, 3]))
                await client.say(f"{players_dict[i].mention} chết nè~")
        else:
            await client.say("Mừng dễ sợ :joy:")
    elif phase == 'day':
        await client.say("Và thế là...")
        await client.say("......")
        await asyncio.sleep(0.5)
        if len(death_list) != 0:    
            for i in death_list:
                await asyncio.sleep(random.choice([1, 2, 3]))
                await client.say(f"... {players_dict[i].mention} đã ra đi...")
        else:
            await client.say("... không ai chết cả! :>")


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

    await client.send_message(players_dict[roles_dict['tree']], "Hãy chọn người bạn muốn treeeeeeee")
    if holder[roles_dict['tree']].status and holder[roles_dict['tree']].role == 'tree':
        rep = await client.wait_for_message(author=players_dict[roles_dict['tree']])
        while rep.content not in players_list:
            try:
                if not holder[rep.content].status:
                    await client.send_message(players_dict[roles_dict['tree']], ":o: Xin hãy chọn người **còn sống**!")
                    continue
            except: pass
            await client.send_message(players_dict[roles_dict['tree']], ":o: Xin hãy chọn người ở trong list!")
            rep = await client.wait_for_message(author=players_dict[roles_dict['tree']])
        if holder[rep.content].role == 'wolf':
            await client.send_message(players_dict[roles_dict['tree']], f"{players_dict[roles_dict['tree']].mention}, **gật gật gật**")
        else:
            await client.send_message(players_dict[roles_dict['tree']], f"{players_dict[roles_dict['tree']].mention}, **lắc lắc lắc**")
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
                await client.send_message(players_dict[i], "Xin hãy chọn người bạn muốn đợp. Nếu không, hãy nhập 'none'.")
                rep = await client.wait_for_message(author=players_dict[i])
                while rep.content not in players_list:
                    if rep.content == 'none': break
                    try:
                        if not holder[rep.content].status:
                            await client.send_message(players_dict[i], ":o: Xin hãy chọn người **còn sống**!")
                            continue
                    except: pass
                    await client.send_message(players_dict[i], ":o: Xin hãy chọn người ở trong list!")
                    rep = await client.wait_for_message(author=players_dict[i])   
                for a in roles_dict['wolf']:
                    if rep.content == 'none':
                        await client.send_message(players_dict[a], f"{players_dict[i].mention} đã **không** vote ai hết!")
                    else:
                        await client.send_message(players_dict[a], f"{players_dict[i].mention} đã vote đợp {rep.content}")
                reps.append(rep.content)
            else:
                sleep(7)

    if rep.content != 'none':
        death = rep.content
    else: death = 'none'
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

    players_list.clear()
    players_dict.clear()
    roles_dict.clear()

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
    box_setup.add_field(name=f'Joined ({int(len(players_list))})', value=', '.join(plists), inline=False)
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


client.run(str(os.environ.get(TOKEN)))
