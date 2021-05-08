from discord import guild
from discord.utils import get
import gitlab
from quart import Quart, request, abort
from bs4 import BeautifulSoup as bs
import discord
import os
import threading
import asyncio
import json

disc_server = ''
message_ids = []
app = Quart(__name__)
client = discord.Client()

url_listen = '127.0.0.1'
port = 7500
projects_to_be_listened = []
post_req=[]
projlistempty = True
@app.route('/', methods=['POST'])
async def route():
    if request.method == 'POST':
        data = await request.data
        post_req.append(data)
        dict_str = data.decode("UTF-8")
        json_dict = json.loads(dict_str)
        loop = asyncio.get_running_loop()
        temp = asyncio.run_coroutine_threadsafe(listen(json_dict), loop)
        return '', 200
    else:
        abort(400)
@client.event
async def on_message(message):
    category= get(message.guild.categories, name = 'issue-discussion')
    categories = []
    global disc_server
    disc_server = message
    message_ids.append(message.id)
    for x in message.guild.categories:
        categories.append(x.name)
    if message.content.startswith('gitbot!issue'):
        if 'issue-discussion'not in categories:
            category = await message.guild.create_category('issue-discussion')   
        elements = str(message.content).split(' ')
        issue_num = int(elements[1])
        project_name = 'openstreetcraft/' + str(elements[2])
        server = gitlab.Gitlab('https://www.gitlab.com', os.getenv('GITLAB_TOKEN'), api_version=4, ssl_verify=False)
        project = server.projects.get(project_name)
        issue = project.issues.get(issue_num)
        new_text_channel = await message.guild.create_text_channel(str(project.name) + ' Issue No. ' + str(issue_num) +' (' + issue.title + ')', category=category)
        await message.channel.send('New channel created, you can find it at ' + new_text_channel.mention)
    elif message.content==('gitbot!ping'):
        #await message.channel.send('Pong ' + str(client.latency))
        '''test = client.get_guild(disc_server)
        await test.create_text_channel('TEST TEST TEST')'''
    elif message.content=='gitbot!help':
        await message.channel.send('gitbot!ping:- Get bot ping\ngitbot!help:- get this dialog\ngitbot!hook:- Open a new text channel for discussing an issue(Usage:- gitbot!hook <issue no.> <project name>)')
    elif message.content=='gitbot!purge':
        channels = category.channels
        for x in channels:
            await x.delete()
        category.delete
    elif message.content.startswith('gitbot!project'):
        elements = str(message.content).split(' ')
        if elements[1] == 'list':
            group = server.groups.get(871066)
            projects_list = group.projects.list()
            print_str = ''
            print(projects_list)
            for x in projects_list:
                print_str = print_str + '\n' + x.name
            embed=discord.Embed(description=print_str, color=0xFF5733)
            await message.channel.send(embed=embed)
        elif elements[1] == 'getid':
            group = server.groups.get(871066)
            projects_list = group.projects.list()
            for x in projects_list:
                if elements[2] == x.name:
                    await message.channel.send(str(x.id))
                else:
                    continue
        elif elements[1] == 'listall':
            group = server.groups.get(871066)
            projects_list = group.projects.list()
            print_str = ''
            print(projects_list)
            for x in projects_list:
                x = server.projects.get(x.id)
                print_str = print_str + '\n' + x.name +'(' +str(len(x.issues.list())) +')'
            embed=discord.Embed(description=print_str, color=0xFF5733)
            await message.channel.send(embed=embed)
    elif message.content==('wee'):
        await message.delete()
        await message.channel.send('<a:peepowee:837934652920299530>')
    elif message.content.startswith('gitbot?purge'):
        elements = str(message.content).split(' ')
        msg_num = int(elements[1])
        for x in range(0, msg_num + 1):
            msg = await message.channel.fetch_message(message_ids[-1])
            await msg.delete()
            message_ids.pop(-1)
    elif message.content.startswith('gitbot!hook'):
        server = gitlab.Gitlab('https://www.gitlab.com', os.getenv('GITLAB_TOKEN'), api_version=4, ssl_verify=False)
        elements = str(message.content).split(' ')
        projects_to_be_listened.append(server.projects.get(int(elements[1])))
        await message.channel.send('Please add {} as the webhook url.'.format(url_listen))
        projlistempty = False 
async def listen(listen_json):
    if listen_json['object_kind'] == 'issue':
        username = listen_json['user']['username']
        issue_id = listen_json['object_attributes']['iid']
        issue_title = listen_json['object_attributes']['title']
        issue_desc = listen_json['object_attributes']['description']
        print(issue_title)
        #loop = asyncio.new_event_loop().run_until_complete(make_channel(issue_title))
        print(disc_server)
        server = client.get_guild(disc_server.guild.id)
        print(server)    
        channel = await disc_server.guild.create_text_channel(issue_title)
        print(channel)

def discord_run():
    client.run('DISCORD_TOKEN')
def listener_run():
    app.run(port=7500)
t1 = threading.Thread(target=discord_run)
t2= threading.Thread(target=listener_run)
t1.start()
t2.start()
t1.join()
t2.join()
