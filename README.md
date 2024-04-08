# Online-socket-quiz
The game involves up to four players engaging with a host (server) who possesses a comprehensive list of questions along with their correct answers. A randomly selected question is dispatched to all players simultaneously. Players vie to answer by pressing the 'Enter' key on their keyboards. The first player to buzz in within a 10-second timeframe earns the opportunity to respond to the question. If no player buzzes in within the allocated time, the host proceeds to the next question.
Upon buzzing in, the player must provide their answer within 10 seconds. If the response aligns with the correct answer, the player earns a point. However, failure to provide an answer within the given time frame, offering an incorrect answer, or providing a response other than the designated option number incurs a deduction of 0.5 points. Following each response, the host progresses to the subsequent question.
The game concludes when any player accumulates 5 points or more, upon which they are declared the victor.
## Instructions to run:
Start the server with the following command: python3 server.py <IP_address> <Port_Number>

Start the client with the following command: python3 client.py <IP_address> <Port_Number>
