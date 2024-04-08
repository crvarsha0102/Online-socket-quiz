import socket
import select
import random
import sys
import time
from Questions import Q_and_A
from _thread import *

MSG_LEN = 5
random.shuffle(Q_and_A)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

num_players = int(input("Please enter the number of participants (maximum allowed is 4): "))
players_joined = 0

if num_players > 4 or num_players < 1:
    while num_players > 4 or num_players < 1:
        num_players = int(input("Please input a valid number: "))

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server_socket.bind((IP_address, Port))
server_socket.listen(10)
print("Server started!")

print(f"Waiting for connection on IP address and Port number: {IP_address}, {Port}")

clients_list = []
participants = {}
scores = {}
mapping = {}
current_player = [server_socket]
correct_answer = [-1]

def receive_message(client_sock):
    message = client_sock.recv(1024).decode('utf-8')
    return message

def send_to_one(receiver, message):
    message = f"{len(message):<{MSG_LEN}}" + message
    try:
        receiver.send(bytes(message, 'utf-8'))
    except:
        receiver.close()
        clients_list.remove(receiver)

def send_to_all(sender, message):
    message = f"{len(message):<{MSG_LEN}}" + message
    for client in clients_list:
        if (client != server_socket and client != sender):
            try:
                client.send(bytes(message, 'utf-8'))
            except:
                client.close()
                clients_list.remove(client)

def update_scores(player, points):
    print(participants[mapping[player]])
    scores[participants[mapping[player]]] += points
    print(scores)
    send_to_all(server_socket, "\nScore: ")
    for player_name in scores:
        send_to_all(server_socket, ">> " + str(player_name) + ": " + str(scores[player_name]))

def end_quiz():
    send_to_all(server_socket, "GAME OVER\n")
    print("GAME OVER\n")
    for player_name in scores:
        if scores[player_name] >= 5:
            send_to_all(server_socket, "WINNER: " + str(player_name))
    send_to_all(server_socket, "Scoreboard:")
    print("Scoreboard: ")
    for player_name in scores:
        send_to_all(server_socket, ">> " + str(player_name) + ": " + str(scores[player_name]))
        print(">> " + str(player_name) + ": " + str(scores[player_name]))
    sys.exit()

def ask_question():
    if len(Q_and_A) != 0:
        question_and_answer = Q_and_A[0]
        question = question_and_answer[0]
        options = question_and_answer[1]
        answer = question_and_answer[2]

        random.shuffle(options)
        option_number = 1

        send_to_all(server_socket, "\nQ. " + str(question))
        print("\nQ. " + str(question))
        for option in options:
            send_to_all(server_socket, "   " + str(option_number) + ") " + str(option))
            print("   " + str(option_number) + ") " + str(option))
            if option == answer: 
                correct_answer.pop(0)
                correct_answer.append(int(option_number))
            option_number += 1
        send_to_all(server_socket, "\nHit Enter to answer")
        print("Correct answer: option number " + str(correct_answer))
    else:
        send_to_all(server_socket, "All questions have been asked!")
        end_quiz()
        sys.exit()

def quiz():
        current_player[0] = server_socket
        random.shuffle(Q_and_A)
        ask_question()
        key_press = select.select(clients_list, [], [], 10)
        if len(key_press[0]) > 0:
            buzzer_pressed_by = key_press[0][0]
            send_to_one(buzzer_pressed_by, "YOU PRESSED THE BUZZER")
            send_to_one(buzzer_pressed_by, "ENTER YOUR ANSWER: ")
            send_to_all(buzzer_pressed_by, "BUZZER PRESSED")
            print("BUZZER PRESSED")
            time.sleep(0.01)
            current_player.pop(0)
            current_player.append(buzzer_pressed_by)
            start_time = time.time()
            Q_and_A.pop(0)

            answering = select.select(current_player, [], [], 10)
            if len(answering) > 0:
                if time.time() - start_time >= 10:
                    send_to_one(buzzer_pressed_by, "NOT ANSWERED!")
                    send_to_all(server_socket, str(participants[mapping[buzzer_pressed_by]]) + " -0.5")
                    print(str(participants[mapping[buzzer_pressed_by]]) + " -0.5")
                    update_scores(buzzer_pressed_by, -0.5)
                    time.sleep(3)
                    quiz()
                else:
                    time.sleep(3)
                    quiz()
            else:
                print("NOTHING!")                       
        else:
            send_to_all(server_socket, "BUZZER NOT PRESSED")
            print("BUZZER NOT PRESSED")
            time.sleep(3)
            Q_and_A.pop(0)
            quiz()

clients_list.append(server_socket)

while True:
    rList, wList, error_sockets = select.select(clients_list, [], [])
    for client_socket in rList:
        if client_socket == server_socket:
            conn, addr = server_socket.accept()
            if players_joined == num_players:
                send_to_one(conn, "Maximum number of players joined!")
                conn.close()
            else:
                name = receive_message(conn)
                if name:
                    if name in participants.values():
                        send_to_one(conn, "Name already taken. Please choose a different one and join again!")
                        conn.close()
                    else:
                        participants[conn] = name
                        scores[name] = 0
                        players_joined += 1
                        mapping[conn] = addr
                        clients_list.append(conn)
                        print("Participant connected: " + str(addr) +" [ " + participants[conn] + " ]" )
                        if players_joined < num_players:
                            send_to_one(conn, "Welcome to the quiz " + name + "!\nPlease wait for other participants to join...")
    
                        if players_joined == num_players:
                            send_to_all(server_socket, "\nParticipant(s) joined:")
                            for participant_addr in participants:
                                send_to_all(server_socket,">> " + participants[participant_addr])
                            send_to_all(server_socket, "\nThe quiz will begin in 30 seconds. Quickly go through the instructions\n")
                            send_to_all(server_socket, "INSTRUCTIONS:\n> For each question, you will have 10 seconds to press the buzzer.\n> To press the buzzer, hit Enter.\n> After pressing the buzzer, you will have 10 seconds to answer the question.\n\n> You will be awarded 1 point if you provide the correct option number after pressing the buzzer first\n\n> 0.5 points will be deducted in the following cases:\n  > If you press the buzzer first and give the wrong answer\n  > If you press the buzzer first but don't give an answer\n  > If you provide any other answer other than the option numbers (1 to 4)\n\n> The first person to score 5 points or more is the winner\n\nALL THE BEST!")
                            print("\n" + str(num_players) + " participant(s) connected! The quiz will begin in 30 seconds")
                            time.sleep(30)
                            start_new_thread(quiz, ())
        else:
            msg = receive_message(client_socket)
            print(msg)
            if client_socket == current_player[0]:
                try:
                    user_ans = int(msg)
                    if user_ans == correct_answer[0]:
                        send_to_one(client_socket, "CORRECT ANSWER")
                        send_to_all(server_socket, str(participants[mapping[client_socket]]) + " +1")
                        print(str(participants[mapping[client_socket]]) + " +1")
                        update_scores(client_socket, 1)
                        current_player[0] = server_socket
                        if scores[participants[mapping[client_socket]]] >= 5:
                            end_quiz()
                                        
                    else:
                        send_to_one(client_socket, "WRONG ANSWER")
                        send_to_all(server_socket, str(participants[mapping[client_socket]]) + " -0.5")
                        print(str(participants[mapping[client_socket]]) + " -0.5")
                        update_scores(client_socket, -0.5)
                        current_player[0] = server_socket
                except ValueError:
                    send_to_one(client_socket, "INVALID OPTION")
                    send_to_all(server_socket, str(participants[mapping[client_socket]]) + " -0.5")
                    print(str(participants[mapping[client_socket]]) + " -0.5")
                    update_scores(client_socket, -0.5)
                    current_player[0] = server_socket        

            elif current_player[0] != server_socket:
                send_to_one(client_socket, "TOO LATE!")
            
    client_socket.close()
server_socket.close()
