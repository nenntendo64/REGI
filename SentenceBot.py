# This bot takes the chat history from a discord channel and then sends generated
# sentences based on a Markov model for speech synthesis.
# To get started, check out here: https://discordpy.readthedocs.io/en/latest/intro.html#installing
# Documentation for markovify is here: https://github.com/jsvine/markovify
#
# Made by Hunter Nenneau (nenntendo64)

import discord
import random
import time
#import I2C_LCD_driver
import markovify
import asyncio
from discord.ext import tasks


message_tosend='Hello!'
lst = []
list1 = []
client = discord.Client()
#Below is the code for adding a 16x2 lcd on a raspberry pi
#link to set this up is https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/
#mylcd = I2C_LCD_driver.lcd()
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global message_tosend
    global lst
    global list1
    global text_model
    global mylcd
    generateModel.start()
    sendMessageToChannel.start()

@client.event
async def on_message(message):
    #mylcd.lcd_clear()
    global message_tosend
    if message.author == client.user:
        return
    # Use this command #scan to scan all the messages in the channel that the command is sent.
    # this is used to create(only once)the messageHistory.txt file and fill it with the chat
    # history.
    elif message.content == "#scan":
        startTime = time.perf_counter()
        async for message in message.channel.history(limit=2000000):
            if message.author != client.user:
                with open('messageHistory.txt', 'a+', encoding="utf-8") as f:
                    if "http" not in message.content:
                        if not message.attachments:
                            if "\n" in message.content:
                                f.write("%s\n" % message.content.replace("\n", ""))
                                #print(message.content)
                            elif message.content == "":
                                print(message.content)
                            else:
                                f.write("%s\n" % message.content)
                                #print(message.content)
    # Wrote this as a helper function, basically send the #save command in any chat
    # and the bot will dump all messages in the message list into the messageHistory.txt to
    # be compiled in the next speech model.
    elif message.content == '#save':
        #mylcd.lcd_clear()
        mylcd.lcd_display_string('Saving', 1)
        with open('messageHistory.txt', "a+" ,encoding="utf-8") as f:
            i = 0
            while i < len(lst):
                if "http" not in lst[i]:
                    if "\n" in lst[i]:
                        f.write("%s\n" % lst[i].replace("\n", ""))
                    elif lst[i] == "":
                        print("")
                    else:
                        f.write("%s\n" % lst[i])
                i+=1
            lst.clear()
            f.close()
            #mylcd.lcd_clear()
            #mylcd.lcd_display_string('Saved!', 1)
    elif('\\' in message.content):
        return
    else:
        lst.append(message.content)
        #mylcd.lcd_display_string('# of Messages:', 1)
        #mylcd.lcd_display_string(str(len(lst)), 2)

##
# This function sends the message to the desired chat every 2 days. You can
# change the for loop to change how many sentences are sent.
@tasks.loop(minutes = 120)
async def sendMessageToChannel():
    #mylcd.lcd_clear()
    #mylcd.lcd_display_string('Speaking', 1)
    # Put the chat ID for the channel that you want the bot to send messages,
    # You can get this by enabling developer mode in discord and right clicking
    # on the channel.
    channel = client.get_channel(798392001698857000)
    message_tosend = ""
    for i in range(5):
        message_tosend+=text_model.make_sentence()
        message_tosend+=" \n"



    await channel.send(message_tosend)

# This function is called at start up, and then again every 2 days. It clears
# The list of messages and writes them to the messageHistory.txt, it then uses
# markovify to generate the speech model.
@tasks.loop(minutes = 2881)
async def generateModel():
    #mylcd.lcd_clear()
    #mylcd.lcd_display_string('Generating Model', 1)
    global text_model
    with open('messageHistory.txt', "a+" ,encoding="utf-8") as f:
        i = 0
        while i < len(lst):
            if "http" not in lst[i]:
                if "\n" in lst[i]:
                    f.write("%s\n" % lst[i].replace("\n", ""))
                elif lst[i] == "":
                    print("")
                else:
                    f.write("%s\n" % lst[i])
            i+=1
        lst.clear()
        f.close()
        with open('messageHistory.txt',encoding="utf-8") as f:
            text = f.read()
            text_model = markovify.NewlineText(text, well_formed = False, state_size = 2)
            f.close()
            text_model = text_model.compile()
    #mylcd.lcd_clear()
    #mylcd.lcd_display_string('Model Complete', 1)
    #mylcd.lcd_display_string('Waiting For MSG', 2)
    await asyncio.sleep(1)


#Below is where your discord bot token goes. To get started go here: https://discordpy.readthedocs.io/en/latest/quickstart.html
client.run('')
