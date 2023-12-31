import random
from spyne.service import ServiceBase
from spyne.decorator import rpc
from spyne.model.primitive import Unicode,Integer
from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

class GameService(ServiceBase):
    #self._hidden_number={}
    _hidden_number=set()
    _result=""
    _player_name = "guess player"
    _nb_attempts = 10

    @rpc(_returns=Unicode(nillable=False))
    #the @rpc decorator is used to specify the metadata of the function that will be included on WSDL file
    def about_game(self):
        return "This is a cow and bull game.\n" \
               "You have to guess a 4-digits hidden number.\n" \
               "all digits are different.\n" \
               "you have 10 attempts.\n" \
               "if you guess a digit in the right place, you get a 'B'.\n" \
               "if you guess a digit in misplace you get a 'C'.\n" \
               "you win if you got '4B'\n" \
               "for example if the hidden number is 1234 and you give 5436." \
               "you get 1B and 1C."

    # @rpc(Unicode(nillable=True),Integer(nillable=True),_returns=Unicode(nillable=False))
    # def start_game(self, player_name="guess player", nb_attempts=10):
    #     GameService._hidden_number=set()
    #     GameService._hidden_number.add(random.randint(1,9))
    #     while(len(GameService._hidden_number)<4):
    #         GameService._hidden_number.add(random.randint(0,9))
    #     GameService._player_name=player_name
    #     if nb_attempts <=10:
    #         GameService._nb_attempts=nb_attempts
    #     else:
    #         return ("Error. The attempts must be less than 10.")
    #     return "the game was initialized."+GameService._player_name+ "You can go.\n"+str(GameService._hidden_number)

    #or using random.shuffle()
    @rpc(Unicode(nillable=True), Integer(nillable=True), _returns=Unicode(nillable=False))
    def start_game(self, player_name="guess player", nb_attempts=10):
        first_digit=random.randint(1,9)
        if first_digit==0:
            first_digit=1+random.randint(1,8)
        other_digits=random.sample(range(10),3)
        random.shuffle(other_digits)
        GameService._hidden_number = set([first_digit]+other_digits)

        GameService._player_name = player_name
        if nb_attempts <= 10:
            GameService._nb_attempts = nb_attempts
        else:
            return "Error. The attempts must be less than 10."

        return "The game was initialized. " + GameService._player_name + " You can go.\n" + str(GameService._hidden_number)



    # @rpc(Integer(nillable=False),_returns=Unicode(nillable=False))
    # def play_game(self,player_proposition):
    #     if GameService._nb_attempts==0:
    #         return "You lost. You have exceeded the maximum attempts."
    #     if GameService._result=='4B':
    #         return "you have already won the game."
    #     try:
    #         proposition=str(player_proposition)
    #         if len(proposition)!=4:
    #             raise ValueError("You must introduce a 4-digit number")
    #         #if not proposition.isdigit():
    #         #  raise TypeError("All characters must be digits")
    #         hidden_number=list(GameService._hidden_number)
    #         nbBull=0
    #         nbCow=0
    #         for i in range(4):
    #             if int(proposition[i])==hidden_number[i]:
    #                 nbBull+=1
    #             elif int(proposition[i]) in GameService._hidden_number:
    #                 #verify if we hadn't already checked for the current digit
    #                 j=0
    #                 while j<i and proposition[j]!=proposition[i]:
    #                     j+=1
    #                 if j==i:
    #                     nbCow+=1
    #         GameService._nb_attempts-=1
    #         if nbBull ==0 and nbCow>0:
    #             GameService._result= str(nbCow)+"C"
    #         elif nbBull>0 and nbCow==0:
    #             GameService._result=str(nbBull)+"B"
    #         else:
    #             GameService._result=str(nbBull)+"B" + "-"+str(nbCow)+"C"
    #         if GameService._result=="4B":
    #             GameService._result+=" "+GameService._player_name+" Congratulations! You have won the game"
    #         return GameService._result
    #     except Exception  as e:
    #         return str(e)

    #or
    @rpc(Integer(nillable=False), _returns=Unicode(nillable=False))
    def play_game(self, player_proposition):
        if GameService._nb_attempts == 1:
            return "You lost. You have exceeded the maximum attempts."
        if GameService._result == '4B':
            return "You have already won the game."

        proposition = str(player_proposition)
        result = GameService.evaluate_proposition(proposition)

        if result == "4B":
            result += " " + GameService._player_name + " Congratulations! You have won the game"

        return result
    @staticmethod
    def evaluate_proposition(proposition):
        try:
            if len(proposition) != 4:
                raise ValueError("You must introduce a 4-digit number")

            hidden_number = list(GameService._hidden_number)
            nbBull, nbCow = 0, 0

            for i in range(4):
                if int(proposition[i]) == hidden_number[i]:
                    nbBull += 1
                elif int(proposition[i]) in GameService._hidden_number:
                    nbCow += 1

            GameService._nb_attempts -= 1

            if nbBull == 0 and nbCow > 0:
                return f"{nbCow}C"
            elif nbBull > 0 and nbCow == 0:
                return f"{nbBull}B"
            else:
                return f"{nbBull}B-{nbCow}C"
        except Exception as e:
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