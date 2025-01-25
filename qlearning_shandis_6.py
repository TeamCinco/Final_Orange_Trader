import csv
import random

# Round a number to 4 decimal places
def round_to_4_decimals(value):
    return round(value, 4)

# Check if TP or SL is reached first and skip to that row
def check_outcome(data, start_index, trade_action):
    entry_price = data[start_index]["Price"]
    atr = data[start_index]["ATR"]

    tp = round_to_4_decimals(entry_price + 2 * atr) if trade_action == "BUY" else round_to_4_decimals(entry_price - 2 * atr)
    sl = round_to_4_decimals(entry_price - 2 * atr) if trade_action == "BUY" else round_to_4_decimals(entry_price + 2 * atr)

    for i in range(start_index + 1, len(data)):
        current_price = data[i]["Price"]
        if (trade_action == "BUY" and current_price >= tp) or (trade_action == "SELL" and current_price <= tp):
            return "TP", i  # Return the result and the row index where it resolves
        if (trade_action == "BUY" and current_price <= sl) or (trade_action == "SELL" and current_price >= sl):
            return "SL", i  # Return the result and the row index where it resolves
    return "No TP or SL", len(data) - 1  # If unresolved, jump to the last row

# Load data from CSV
def load_data(file_name):
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        expected_columns = {"timestamp", "close", "ATR", "volume", "LWPI Value", "ALMA Value", "VIXFIX", "Filtered Stochastic", "Signal", "ATR_EMA", "Price_Difference", "Gradient", "ALMA_Gradient", "ATR_EMA_Gradient", "EMA_13", "EMA_Gradient"}
        if not expected_columns.issubset(reader.fieldnames):
            raise ValueError(f"Missing required columns: {expected_columns - set(reader.fieldnames)}")
        return [
            {
                "Time": row["timestamp"],
                "Price": float(row["close"]),
                "ATR": float(row["ATR"]),
                "Vol": float(row["volume"]),
                "LWPI": float(row["LWPI Value"]),
                "ALMA": float(row["ALMA Value"]),
                "VIX": float(row["VIXFIX"]),
                "Filt_Stoch": float(row["Filtered Stochastic"]),
                "Sig": float(row["Signal"]),
                "ATR_EMA": float(row["ATR_EMA"]),
                "PriceDiff": float(row["Price_Difference"]),
                "Grad": float(row["Gradient"]),
                "ALMA_Grad": float(row["ALMA_Gradient"]),
                "ATR_EMA_Grad": float(row["ATR_EMA_Gradient"]),
                "EMA13": float(row["EMA_13"]),
                "EMA_Grad": float(row["EMA_Gradient"])
            }
            for row in reader
        ]

# Q-learning implementation (barebones)
class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.995):
        self.actions = actions  # possible actions: "BUY", "SELL", "PASS"
        self.learning_rate = learning_rate  # learning rate
        self.discount_factor = discount_factor  # how much future rewards count
        self.exploration_rate = exploration_rate  # exploration vs exploitation
        self.exploration_decay = exploration_decay  # exploration decay rate
        self.q_table = {}  # Initialize Q-table

    def get_state(self, data, index, balance):
        """Return a tuple that represents the state, using all the features and balance."""
        features = (
            round(data[index]["Price"], 4),
            round(data[index]["ATR"], 4),
            round(data[index]["Vol"], 4),
            round(data[index]["LWPI"], 4),
            round(data[index]["ALMA"], 4),
            round(data[index]["VIX"], 4),
            round(data[index]["Filt_Stoch"], 4),
            round(data[index]["Sig"], 4),
            round(data[index]["ATR_EMA"], 4),
            round(data[index]["PriceDiff"], 4),
            round(data[index]["Grad"], 4),
            round(data[index]["ALMA_Grad"], 4),
            round(data[index]["ATR_EMA_Grad"], 4),
            round(data[index]["EMA13"], 4),
            round(data[index]["EMA_Grad"], 4),
            round(balance, 2)  # Include balance in the state
        )
        return features

    def update_q_value(self, state, action, reward, next_state):
        """Update the Q-value for a given state-action pair"""
        old_q_value = self.q_table.get((state, action), 0.0)
        max_future_q = max([self.q_table.get((next_state, a), 0.0) for a in self.actions], default=0.0)
        new_q_value = old_q_value + self.learning_rate * (reward + self.discount_factor * max_future_q - old_q_value)
        self.q_table[(state, action)] = new_q_value

    def choose_action(self, state):
        """Choose an action based on exploration or exploitation"""
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.actions)  # Explore
        else:
            q_values = {action: self.q_table.get((state, action), 0.0) for action in self.actions}
            return max(q_values, key=q_values.get)  # Exploit

    def decay_exploration(self):
        """Decay the exploration rate after each episode"""
        self.exploration_rate *= self.exploration_decay

# Game logic with Q-learning agent
def forex_game(data, episode_num, agent):
    balance = 100  # Starting balance
    print(f"\nEpisode {episode_num + 1}: Starting balance: ${balance}")
    print("Rules: TP = 2×ATR away. SL = 2×ATR away. $1 gained for hitting TP, $1 lost for hitting SL.")
    i = 0  # Start at the first row

    while i < len(data) - 1:
        current_data = data[i]
        atr = current_data["ATR"]
        time = current_data["Time"]

        if atr == 0:
            print(f"\nWarning: ATR is 0 at time {time}. Skipping this row.")
            i += 1
            continue

        # State for the Q-learning agent
        state = agent.get_state(data, i, balance)

        # Agent chooses an action
        action = agent.choose_action(state)

        # Determine reward and next state based on chosen action
        if action == "BUY":
            result, next_index = check_outcome(data, i, "BUY")
            reward = 1 if result == "TP" else -1 if result == "SL" else 0
        elif action == "SELL":
            result, next_index = check_outcome(data, i, "SELL")
            reward = 1 if result == "TP" else -1 if result == "SL" else 0
        else:
            reward = 0
            next_index = i + 1  # No change if PASS

        # Update Q-table based on the result
        next_state = agent.get_state(data, next_index, balance + reward)
        agent.update_q_value(state, action, reward, next_state)

        # Update balance
        balance += reward

        # Restart game if balance drops to $50
        if balance <= 50:
            print("\nBalance dropped to $50. Restarting the game.")
            return balance  # End the current episode

        # Decay exploration rate
        agent.decay_exploration()

        # Move to the next row after the current one
        i = next_index

    return balance

# Load CSV and start game
file_name = "audusd-h1-bid-2003-08-03T21-2024-05-27.csv"  # Replace with your CSV file path
try:
    forex_data = load_data(file_name)

    agent = QLearningAgent(actions=["BUY", "SELL", "PASS"])
    total_balance = 0
    total_points = 0
    for episode in range(100000):
        final_balance = forex_game(forex_data, episode, agent)

        # Point system based on results
        if final_balance > 100:  # Win
            total_points += 1
        else:  # Loss
            total_points -= 2

        total_balance += final_balance
        print(f"Episode {episode + 1} completed. Final Balance: ${final_balance}")

    avg_balance = total_balance / 100
    print("\n🎮 100 Episodes Complete!")
    print(f"Average Balance after 100 episodes: ${avg_balance}")
    print(f"Total Points: {total_points}")
    print("Thanks for playing. Better luck next time (or maybe you're ready for the big leagues)!")
except FileNotFoundError:
    print("Error: The specified CSV file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
