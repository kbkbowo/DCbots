# -*- coding: utf-8 -*-
"""Othello_the_DCbot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pGa4xxJgEokbmw-tsM8OU7G6HPC584pi
"""

import numpy as np
import random
import matplotlib.pyplot as plt
from copy import deepcopy
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from tqdm.notebook import tqdm

#  1:black, -1:white

class Othello() :
    def __init__(self, board="new") :
      if board == "new" :
        self.board = np.zeros((8, 8))
        self.board[3, 3], self.board[4, 4] = (1, 1)
        self.board[3, 4], self.board[4, 3] = (-1, -1)
      else :
        self.board = board
      self.side = 1 # denotes which player is going to make a move now
      self.players = {1:"black", -1:"white"}
      self.passed = False
      self.update_available()
      self.game_over = False
      self.round = 1
      self.msg_queue = f"It's {self.players[self.side]}'s turn now.\n\n"
      self.record = []
      self.winner = 0

    def show(self) :
      alphs = ["A", "B", "C", "D", "E", "F", "G", "H"]
      ids = [i for i in range(8)]
      plt.matshow(self.board, cmap=plt.get_cmap('binary'), alpha=1)
      # plt.grid(c="green", axis="x", which="minor", alpha=0.3, linewidth=1)
      plt.xticks(ids, np.array(ids)+1)
      plt.yticks(ids, alphs)
      plt.savefig("./temp.png")
      # plt.show()
      plt.close()
      


    def search(self, arr) :
        flipped = 0
        arr = list(arr)
        pos = arr.index(9)
        left = arr[:pos]
        right = arr[pos+1:]

        pivot = len(left)-1
        while pivot >= 0 :
          if left[pivot] == self.side*-1 :
            pivot -= 1
          elif left[pivot] == self.side :
            left[pivot:] = [self.side]*(len(left)-pivot)
            flipped += len(left) - pivot - 1
            break
          else :
            break

        pivot = 0  
        while len(right) > pivot :
          if right[pivot] == self.side*-1 :
            pivot += 1
          elif right[pivot] == self.side :
            right[0:pivot] = [self.side]*pivot
            flipped += pivot
            break
          else :
            break

        arr_new = left + [self.side] + right
        return flipped, arr_new
    

    def attempt(self, pos) : # check if the input is available
      if len(pos) != 2 : return 0, self.board
      pos = pos.lower()
      a = False
      if pos[0] in "abcdefgh" and pos[1] in "12345678" :
        a = True  
      elif pos[1] in "abcdefgh" and pos[0] in "12345678" : 
        a = True
        pos = (pos*2)[1:3]
      if not a :
        return 0, self.board

      pos = (ord(pos[0])-97, int(pos[1])-1)
      if self.board[pos[0], pos[1]] != 0 : return 0, self.board
      pseudo_board = deepcopy(self.board)
      pseudo_board[pos[0], pos[1]] = 9
      row = pseudo_board[pos[0],:]
      col = pseudo_board[:,pos[1]]
      x1 = []
      x2 = []
      for i in range(8) :
        p1 = pos[1] - pos[0]
        if 0 <= i+p1 < 8 :
          x1.append(pseudo_board[i, i+p1])
        p2 = pos[1] + pos[0]
        if 0 <= p2-i < 8 :
          x2.append(pseudo_board[i, p2-i])
      a1, row = self.search(row)
      a2, col = self.search(col)
      a3, x1 = self.search(x1)
      a4, x2 = self.search(x2)
      pseudo_board[pos[0],:] = row
      pseudo_board[:,pos[1]] = col

      s1 = "?"
      p1 = pos[1] - pos[0]
      s2 = "?"
      p2 = pos[1] + pos[0]
      for i in range(8) :
        if 0 <= i+p1 < 8 :
          if s1 == "?" : s1 = i
          pseudo_board[i, i+p1] = x1[i-s1]
        if 0 <= p2-i < 8 :
          if s2 == "?" : s2 = i
          pseudo_board[i, p2-i] = x2[i-s2]

      return (a1 + a2 + a3 + a4), pseudo_board


    def update_available(self) :
      self.available = np.zeros((8, 8))
      for j, x in enumerate("12345678") :
        for i, y in enumerate("ABCDEFGH") :
          result = self.attempt(y+x)
          self.available[i, j] = result[0]


    def move(self, pos) :
      a, pseudo_board = self.attempt(pos)
      if a : 
        self.record.append(pos.upper())
        self.board = pseudo_board
        self.side *= -1 
        self.round += 1
        self.msg_queue += f"Made a move at {pos} Successfully!\n"
        self.show()
        self.update_available()
        if (self.available == 0).all() :
          self.side *= -1
          self.update_available()
          if (self.available == 0).all() :
            self.msg_queue += "Both players have nowhere to move now, game over!\n"
            self.game_over = True
            self.endgame()
          else :
            self.msg_queue += f"{self.players[self.side*-1]} has nowhere to move. It's {self.players[self.side]}'s turn again.\n\n"
        else :
          self.msg_queue += f"It's {self.players[self.side]}'s turn now.\n\n"
      else :
        self.msg_queue += f"That's not an available move!\n"


    def endgame(self) :
      black_p = np.count_nonzero(self.board == 1)
      white_p = np.count_nonzero(self.board == -1)
      self.msg_queue += f"Points count : \nblack:white = {black_p}:{white_p}\n"
      if black_p > white_p : 
        self.msg_queue += "Black wins!\n"
        self.winner = 1
      elif black_p == white_p :
        self.msg_queue += "Tie!\n"
      else :
        self.msg_queue += "White wins!\n"
        self.winner = -1
      self.msg_queue += f"本次棋譜:\n{self.record}"

    


class human() :
  def __init__(self) :
    pass
  def make_a_move(self, game) :
    return input()

class bot1() : # God does dot play dice, but this bot always does.
  def __init__(self) :
    pass
  def make_a_move(self, game) :
    candidates = np.where(game.available!=0)
    chosen_idx = random.randint(0, len(candidates[0])-1)
    return chr(candidates[0][chosen_idx]+97) + str(candidates[1][chosen_idx]+1) 


class bot2() : # A prototype bot which is only GREEDY
  def __init__(self) :
    pass
  def make_a_move(self, game) :
    candidates = np.where(game.available==np.amax(game.available))
    chosen_idx = random.randint(0, len(candidates[0])-1)
    return chr(candidates[0][chosen_idx]+97) + str(candidates[1][chosen_idx]+1)


class bot3() : # A moderate bot with somehow greedy strategy and knows the importance of getting control of the edges
  def __init__(self) :
    corner = np.zeros((8, 8))
    corner[0, 0], corner[0, 7], corner[7, 0], corner[7, 7] = (1, 1, 1, 1)
    self.corner = corner
    side = np.zeros((8, 8))
    side[0,:] = 1
    side[7,:] = 1
    side[:,0] = 1
    side[:,7] = 1
    side = side - corner
    self.side = side     
  def make_a_move(self, game) :
    if (self.corner*game.available != 0).any() :
      candidates = np.where(self.corner*game.available != 0)
    elif (self.side*game.available != 0).any() :
      candidates = np.where(self.side*game.available != 0)
    elif game.round < 20 :
      candidates = np.where(game.available==np.amin(game.available + (game.available==0)*20))
    else : 
      candidates = np.where(game.available==np.amax(game.available))
    chosen_idx = random.randint(0, len(candidates[0])-1)
    chosen = chr(candidates[0][chosen_idx]+97) + str(candidates[1][chosen_idx]+1)
    print(chosen)
    return chosen

class bot4() :
  def __init__(self, network) : 
    self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    self.decision_nn = network.to(self.device)
    self.reverted = False
  def make_a_move(self, game) :
    board = torch.from_numpy(game.board * game.side).float().to(self.device)
    with torch.no_grad() :
      self.decision_nn.eval()
      mat = self.decision_nn(board).cpu() * torch.from_numpy(np.sign(game.available))
      self.decision_nn.train()
    if (mat.detach().numpy() == 0).all() :
      return bot1().make_a_move(game)
    chosen = int(torch.argmax(mat))
    return chr(chosen//8+97) + str(chosen%8+1)

class Qnetwork(nn.Module) :
  def __init__(self) :
    super().__init__()
    self.fc = nn.Sequential(
        nn.Linear(64, 256),
        nn.ReLU(),
        nn.Linear(256, 1024),
        nn.ReLU(),
        nn.Linear(1024, 512),
        nn.ReLU(),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Linear(256, 64),
        nn.ReLU()
    )
  def forward(self, x) :
    x = x.view(-1, 64)
    x = self.fc(x)
    return x.view(-1, 8, 8)

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="/")

@bot.event
async def on_ready():
  print(">>Bot is online...<<")


mode = "idle"
@bot.event
async def on_message(msg):
  if msg.channel != bot.get_channel(862154839152132096):
    return
  if msg.content == "init" :
    global game
    global mode
    global player_list
    global players
    global colors
    mode = "idle"
    PATH = "./best_network_info"
    device = "cuda"
    net = Qnetwork().to(device)
    checkpoint = torch.load(PATH)
    net.load_state_dict(checkpoint["network"])
    player_list = {
        "human" : "human", 
        "bot1" : bot1(),
        "bot2" : bot2(),
        "bot3" : bot3(),
        "bot4" : bot4(net)
    }
    players = { 1:"human", -1:"human" }
    colors = { 1:"black", -1:"white"}
    await msg.channel.send("初始化已完成")
  elif "player_cfg" in msg.content :
    args = msg.content.split(" ")[1:]
    print(args)
    if len(args) != 2 : 
      await msg.channel.send("格式錯誤，請完整輸入\nplayer_cfg 黑子玩家 白子玩家")
      return
    if not (args[0] in player_list.keys() and args[1] in player_list.keys()) :
      await msg.channel.send(f"格式錯誤，目前可用的玩家類型如下:\n{player_list.keys()}")
      return
    players[1], players[-1] = (args[0], args[1])
    await msg.channel.send(f"已設定玩家為 黑:{args[0]}, 白:{args[1]}") 

  elif mode == "idle" and msg.content == "new" :
    await msg.channel.send('正在開新局...')
    game = Othello()
    mode = "playing"
    game.show()
    img = discord.File("./temp.png")
    await msg.channel.send(file=img)
    await msg.channel.send(game.msg_queue)
    game.msg_queue = ""

  elif mode == "paused" and msg.content == "continue" :
    mode = "playing"
    await msg.channel.send("繼續遊玩~~") 

  elif mode == "playing" :
    if "bot" in players[game.side] and colors[game.side]+"'s turn" in msg.content:
      move = player_list[players[game.side]].make_a_move(game)
      await msg.channel.send(f"bot : {move}")
      game.move(move)
      game.show()
      img = discord.File("./temp.png")
      await msg.channel.send(file=img)
      await msg.channel.send(game.msg_queue)
      game.msg_queue = ""
    elif msg.content == "stop" :
      await msg.channel.send("停止遊戲~~")
      mode = "idle"
    elif msg.content == "pause" :
      mode = "paused"
      await msg.channel.send("遊戲暫停~~")
    elif len(msg.content) == 2 :
      game.move(msg.content)
      game.show()
      img = discord.File("./temp.png")
      await msg.channel.send(file=img)
      await msg.channel.send(game.msg_queue)
      game.msg_queue = ""
  



    

bot.run('your token')
