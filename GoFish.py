import random
import socket

# Define the manager class
class Manager:
    def __init__(self, port_range_start, port_range_end):
        self.port_range_start = port_range_start
        self.port_range_end = port_range_end
        self.players = []
        self.deck = self.initialize_deck()  # Initialize a deck of cards
        self.current_port = port_range_start

    def get_next_available_port(self):
        # Get the next available port within the specified range
        if self.current_port <= self.port_range_end:
            port = self.current_port
            self.current_port += 1
            return port
        else:
            return None

    def register_player(self, player_name, player_address, m_port, r_port, p_port):
        # Implement player registration logic here
        player_info = {
            "name": player_name,
            "address": player_address,
            "m_port": m_port,
            "r_port": r_port,
            "p_port": p_port
        }
        if player_name not in [player["name"] for player in self.players]:
            self.players.append(player_info)
            return "SUCCESS"
        else:
            return "FAILURE"

    def query_players(self):
        num_players = len(self.players)
        player_info = self.players
        return num_players, player_info

    def query_games(self):
        # You need to maintain a list of ongoing games and return information about each game
        num_games = len(self.games)
        games_info = self.games
        return num_games, games_info

   

    def start_game(self):
        # Check if there are at least 2 players to start the game
        if len(self.players) < 2:
            return "Not enough players to start the game. You need at least 2 players."

        # Shuffle the deck of cards
        random.shuffle(self.deck)

        # Determine how many cards each player should get
        num_players = len(self.players)
        num_cards_per_player = len(self.deck) // num_players

        # Create a socket for the manager to listen to player connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', self.port))
            server_socket.listen()

            # Inform players that the game has started and send them their cards
            for i in range(num_players):
                player_name, player_address, m_port = self.players[i]
                player_cards = self.deck[i * num_cards_per_player: (i + 1) * num_cards_per_player]
                
                # Create a socket connection to the player
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as player_socket:
                    player_socket.connect((player_address, m_port))
                    
                    # Notify the player about the game start
                    player_socket.sendall("The game has started. You can begin playing.".encode("utf-8"))

                    # Send the player their cards
                    player_socket.sendall(",".join(player_cards).encode("utf-8"))

                    print(f"Player {player_name} received cards: {', '.join(player_cards)}")

        return "Game has started. Players have received their cards."


    def initialize_deck(self):
        # Generate a deck of cards
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        deck = [f"{rank} of {suit}" for rank in ranks for suit in suits]
        return deck

    def end_game(self, game_identifier, player_name):
        # Check if the game exists
        if game_identifier not in self.games:
            return "FAILURE: Game not found"

        game = self.games[game_identifier]

        # Check if the player is the dealer (game creator)
        if player_name != game['dealer']:
            return "FAILURE: You are not the dealer of this game"

        # Determine the winner and update game information
        winner = self.determine_winner(game)
        game['winner'] = winner
        game['status'] = "ended"


        return "SUCCESS: Game has ended. The winner is " + winner
    
    def determine_winner(self, game):
        # You need to determine the winner based on books
        players = game['players']
        max_books = 0
        winner = None

        for player in players:
            player_books = len(player.books)
            if player_books > max_books:
                max_books = player_books
                winner = player.name

        if winner is not None:
            return winner
        else:
            return "No winner"


    def de_register_player(self, player_name):
    # Implement player de-registration logic here
        for player in self.players:
            if player["name"] == player_name:
                # Check if the player is not part of any ongoing game
                if not self.is_player_in_ongoing_game(player_name):
                    self.players.remove(player)
                    return "SUCCESS"
                else:
                    return "FAILURE: Player is in an ongoing game"
        
        return "FAILURE: Player not found"

    def is_player_in_ongoing_game(self, player_name):
        # Check if the player is part of any ongoing game
        for game in self.games:
            if game["dealer"] == player_name or player_name in game["players"]:
                return True
        return False

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(("localhost", self.port))
        while True:
            data, address = server_socket.recvfrom(1024)
            message = data.decode("utf-8")
            response = self.handle_message(message)
            server_socket.sendto(response.encode("utf-8"), address)

    def handle_message(self, message):
        # Handle incoming messages based on the command
        parts = message.split()
        command = parts[0]

        if command == "register":
            # Parse the registration message and call register_player method
            player_name, player_address, m_port, r_port, p_port = parts[1:]
            return self.register_player(player_name, player_address, int(m_port), int(r_port), int(p_port))

        elif command == "query_players":
            # Call query_players method and return the result
            return str(self.query_players())

        elif command == "query_games":
            # Call query_games method and return the result
            return str(self.query_games())

        elif command == "start_game":
            # Parse the start game message and call start_game method
            player_name, k = parts[1:]
            return " ".join(self.start_game(player_name, int(k)))

        elif command == "end_game":
            # Parse the end game message and call end_game method
            game_identifier, player_name = parts[1:]
            return self.end_game(game_identifier, player_name)

        elif command == "de-register":
            # Call de_register_player method
            player_name = parts[1]
            return self.de_register_player(player_name)

        else:
            return "Invalid command"



class Player:
    def __init__(self, manager_address, manager_port, player_name, m_port, r_port, p_port):
        self.manager_address = manager_address
        self.manager_port = manager_port
        self.player_name = player_name
        self.m_port = m_port
        self.r_port = r_port
        self.p_port = p_port

    def register_with_manager(self):
        # Implement registration with manager logic here
        registration_message = f"register {self.player_name} {self.m_port} {self.r_port} {self.p_port}"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(registration_message.encode("utf-8"), (self.manager_address, self.manager_port))
            response, _ = client_socket.recvfrom(1024)
            return response.decode("utf-8")

    def start_game(self, k):
        # Implement starting a game logic here
        start_game_message = f"start_game {self.player_name} {k}"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(start_game_message.encode("utf-8"), (self.manager_address, self.manager_port))
            response, _ = client_socket.recvfrom(1024)
            parts = response.decode("utf-8").split()
            if parts[0] == "SUCCESS":
                game_identifier = parts[1]
                game_players = parts[2:]
                # Implement your game logic here
                # You can start the game and interact with other players
                self.play_game(game_identifier, game_players)
                return "Game started successfully."
            else:
                return "Failed to start the game."
            
            
    def check_for_books(self):
        rank_counts = {}
        for card in self.hand:
            rank = card[0]  # Assuming cards are represented as (rank, suit)
            if rank in rank_counts:
                rank_counts[rank] += 1
            else:
                rank_counts[rank] = 1

        for rank, count in rank_counts.items():
            if count == 4:
                # Found a book, remove the cards from the player's hand
                self.books.append(rank)
                self.hand = [card for card in self.hand if card[0] != rank]


    def play_game(self, game_identifier, game_players):
        try:
            # Connect to the manager for game communication
            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            game_socket.connect((self.manager_address, self.p_port))

            while True:
                # Implement the game play logic here
                user_input = input("Enter your move: ")
                game_socket.send(user_input.encode())
                response = game_socket.recv(1024).decode()
                print("Received from the game:", response)

                if response == "Game over":
                    break

        except Exception as e:
            print(f"An error occurred during game play: {e}")
        finally:
            game_socket.close()

    def run(self):
        try:
            # Register the player with the manager
            registration_result = self.register_with_manager()
            print(f"Registration with manager result: {registration_result}")

            if registration_result != "SUCCESS":
                # If registration fails, handle the error or exit the program as needed
                print("Player registration failed. Exiting...")
                return

            while True:
                # Add user interactions or game-related logic here
                print("Choose an option:")
                print("1. Start a game")
                print("2. Play a game")
                print("3. Exit")

                choice = input("Enter your choice: ")

                if choice == "1":
                    k = int(input("Enter the game parameter (k): "))
                    self.start_game(k)
                elif choice == "2":
                    self.play_game()
                elif choice == "3":
                    # De-register the player before exiting
                    self.de_register_player()
                    print("Player de-registration completed. Exiting...")
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")
    
        except Exception as e:
            print(f"An error occurred: {e}")


# Entry point for manager and player
if __name__ == "__main__":
    manager = Manager(44000, 44499)  # Specify the desired port range
    player = Player("localhost", 5000, "Player1", manager.get_next_available_port(), manager.get_next_available_port(), manager.get_next_available_port())

    # Start the manager and player functionality by calling their respective run methods
    manager.run()
    player.run()

