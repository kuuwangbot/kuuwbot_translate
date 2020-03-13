import config
import irc.bot
import requests
import sys, re
from googletrans import Translator
translator = Translator()


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id  
        self.token = token  
        self.channel = '#' + channel  

        url = 'https://api.twitch.tv/kraken/users?login=' + channel  
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}  
        r = requests.get(url, headers=headers).json()  
        self.channel_id = r['users'][0]['_id']  
        
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('서버 ' + server + ', 포트 ' + str(port) + '에 연결중...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + token)], username, username)  
  
    def on_welcome(self, c, e):  
        print(self.channel + '에 연결되었습니다.')  
  
        c.cap('REQ', ':twitch.tv/membership')  
        c.cap('REQ', ':twitch.tv/tags')  
        c.cap('REQ', ':twitch.tv/commands')  
        c.join(self.channel)  

    def on_pubmsg(self, c, e):  
        # If a chat message starts with an exclamation point, try to run it as a command

        
        sender = e.tags[3]['value']
        
        msg = ''.join(e.arguments)
        emoji_detector = msg.split(' ')
        emoji_file = open("emoji.txt", "r")
        emoji_list = emoji_file.readlines()
        emoji_list[:] = [emoji.rstrip('\n') for emoji in emoji_list]
        
        rm_emt = [word for word in emoji_detector if word not in emoji_list]
        msg = ' '.join(rm_emt)
        if emoji_detector[0][:1] != '!':
            if emoji_detector[0][:6] not in str(emoji_list):
                tr_detect = translator.detect(msg)
                if str(tr_detect)[14:16] != 'ko':     
                    tr_results = translator.translate(msg, dest='ko')
                    c.privmsg(self.channel, e.tags[3]['value'] + '(' + tr_results.src + ')' + ' -> ' + tr_results.text)
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0][1:]
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection
        
        cmd = cmd.split(' ')
        if cmd[0] == "등록":
            with open("emoji.txt", "a+") as f:
                if cmd[1] not in f.read():
                    f.write(cmd[1] + "\n")
                    c.privmsg(self.channel, cmd[1]+ ' -> ' + ' 번역리스트에서 제외되었습니다.')
                    raise ValueError
    
            
def main():
    username = config.twitch['bot']
    client_id = config.twitch['clientID']
    token = config.twitch['oauth']
    channel = config.twitch['ch_fp']
    bot = TwitchBot(username, client_id, token, channel)
    while True:
        try:
            bot.start()  
        except ValueError:
            pass
        except TypeError:
            pass

if __name__ == "__main__":  
    main()    
