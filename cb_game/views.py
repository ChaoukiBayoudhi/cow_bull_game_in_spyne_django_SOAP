from django.shortcuts import render
from spyne.service import ServiceBase
from spyne.decorator import rpc
from spyne.model.primitive import Unicode,Integer
from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt

import random
# Create your views here.
class GameService(ServiceBase):
    
    
    _hidden_number={}
    _result=""

    @rpc(_returns=Unicode(nillable=False))
    def about(self):
        return "This is the game of Cow and Bull.\n" \
            "You have to guess a 4-digit number (all digits are different). \n" \
                "each time, you have to propose a number.\n" \
                    "if a proposed digit is in the right place you'll got 'B', " \
                        "if the digit is misplaced you'll got 'C'\n" \
                            "You win if get '4B'." \
                                "You lose if you attends 10 attempts.\n'" \
                                "For example, if the hidden number is 5429" \
                                "and you give 1432 you'll got 1C and 1B."

    @rpc(Unicode(nillable=True),Integer(nillable=True),_returns=Unicode(nillable=False))
    def start_game(self,player_name="guess player", nb_attempts=10):
        GameService._hidden_number.add(random.randint(1,9))
        while len(GameService._hidden_number)<4:
            GameService._hidden_number.add(random.randint(0,9))

        GameService._player_name=player_name
        if nb_attempts<1 or nb_attempts>10:
            return "Error! The number of attempts must be between 1 and 10."
        GameService._nb_attempts=nb_attempts
        return "The game was initialized. You can go."

    @rpc(Integer(nillable=False),_returns=Unicode(nillable=False))
    def play_game(self,player_proposition):
        if GameService._nb_attempts==0:
            return "You lost. You have exceeded the maximum attempts."
        if GameService._result=='4B':
            return "you have already won the game."
        try:
          proposition=str(player_proposition)
          if len(proposition)!=4:
              raise ValueError("You must introduce a 4-digit number")
          #if not proposition.isdigit():
            #  raise TypeError("All characters must be digits")
          hidden_number=list(GameService._hidden_number)
          nbBull=0
          nbCow=0
          for i in range(4):
              if int(proposition[i])==hidden_number[i]:
                  nbBull+=1
              elif int(proposition[i]) in GameService._hidden_number:
                  #verify if we hadn't already checked for the current digit
                  j=0
                  while j<i and proposition[j]!=proposition[i]:
                      j+=1
                  if j==i:
                      nbCow+=1
          GameService._nb_attempts-=1
          if nbBull ==0 and nbCow>0:
              GameService._result= str(nbCow)+"C"
          elif nbBull>0 and nbCow==0:
              GameService._result=str(nbBull)+"B"
          else:
              GameService._result=str(nbBull)+"B" + "-"+str(nbCow)+"C"
          if GameService._result=="4B":
              GameService._result+=GameService._player_name+" Congratulations! You have won the game"
          return GameService._result
        except Exception  as e:
          return str(e)

#Create the Django Application to be called remotely
#using Soap11, lxml and the GameService class
spyne_app=Application(
  [GameService],
  #target namespace
  #it contains the tags (like <play_game>,</play_game>, ....) definitions
  tns='http://isg.soa.game.tn',
  #lxml is a library to check the XML, HTML and XHTML definitions
  in_protocol=Soap11(validator='lxml'), #for The SOAP-REQUEST Entity
  out_protocol=Soap11() #for The SOAP-RESPONSE Entity
)
#create the DjangoApplication instance
django_app=DjangoApplication(spyne_app)
#create the instance that will be used to respond to The SOAP-REQUESTs
cb_game_app=csrf_exempt(django_app)