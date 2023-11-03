from suds.client import Client

#Create a new instance of the client using Client class of suds
soap_client=Client("http://127.0.0.1:8000/cb_game/?wsdl")

#call the remote method about_game() of the cb_game application
#implemented using spyne library
print(soap_client.service.about_game())

#get the player name and the number of attempts from the user
player_name=input("Enter the player name : ")
nb_attempts=int(input("Number of attempts : "))

#call the remote method start_game() of the cb_game application
result=soap_client.service.start_game(player_name,nb_attempts)
print(result)

#check if the game was successful initialized
if "The game was initialized" in result:
    #repeat indefinitely until the game is over :
    #the player find the hidden number or the number of attempts is depleted
    while True:
        proposition=input("Enter your Proposition : ")
        result=soap_client.service.play_game(proposition)
        print(result)
        #if the result contains the word "Congratulations", we stop the game
        if "Congratulations" in result:
            break

        if "You lost" in result:
            break