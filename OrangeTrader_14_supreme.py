import csv

# Load data from CSV
def load_data(file_name):
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        expected_columns = {"timestamp", "close", "ATR"}
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

# Round a number to 4 decimal places
def round_to_4_decimals(value):
    return round(value, 4)

# Check if TP or SL is reached first and skip to that row
def check_outcome(data, start_index, trade_action, tp, sl):
    entry_price = data[start_index]["Price"]

    for i in range(start_index + 1, len(data)):
        current_price = data[i]["Price"]
        if (trade_action == "BUY" and current_price >= tp) or (trade_action == "SELL" and current_price <= tp):
            return "TP", i  # Return the result and the row index where it resolves
        if (trade_action == "BUY" and current_price <= sl) or (trade_action == "SELL" and current_price >= sl):
            return "SL", i  # Return the result and the row index where it resolves
    return "No TP or SL", len(data) - 1  # If unresolved, jump to the last row

# Game logic with RRR input for TP adjustment and win/loss amount modification
def forex_game(data):
    balance = 100  # Starting balance
    score = 0  # Initialize score
    consecutive_wins = 0  # Track consecutive wins
    print("Welcome to the Forex Game! Make your buy/sell calls and see if you can grow your balance.")
    print("Rules: TP and SL are based on ATR (Average True Range).")
    print("Bonus: +3 for every 2 trades won in a row.")
    i = 0  # Start at the first row
    raise_amount = 0  # Track how much the player has raised in total
    row_threshold = 5760  # Number of rows per batch
    batch = 1  # Starting batch
    profit_2880 = 0  # Track profit after every 2880 rows
    start_balance = balance  # Save the initial balance to track profit over 2880 rows

    while i < len(data) - 1:
        # Current row data
        current_data = data[i]
        current_price = current_data["Price"]
        atr = current_data["ATR"]
        time = current_data["Time"]

        if atr == 0:
            print(f"\nWarning: ATR is 0 at time {time}. Skipping this row.")
            i += 1  # Skip this row if ATR is zero
            continue

        # Displaying current data
        print(f"\nTime: {time} | Price: {current_price} | ATR: {atr}")
        print(f"Current Balance: ${balance} | Score: {score}")
        print(f"Volume: {current_data['Vol']} | LWPI: {current_data['LWPI']} | ALMA: {current_data['ALMA']} | VIX: {current_data['VIX']}")
        print(f"Filt_Stoch: {current_data['Filt_Stoch']} | Sig: {current_data['Sig']} | ATR_EMA: {current_data['ATR_EMA']}")
        print(f"PriceDiff: {current_data['PriceDiff']} | Grad: {current_data['Grad']} | ALMA_Grad: {current_data['ALMA_Grad']}")
        print(f"ATR_EMA_Grad: {current_data['ATR_EMA_Grad']} | EMA13: {current_data['EMA13']} | EMA_Grad: {current_data['EMA_Grad']}")

        # Player input for action
        action = input("Do you want to [B]uy, [S]ell, or [P]ass? ").strip().upper()

        if action in ["B", "S"]:
            # Ask for RRR input only after action is chosen
            rrr_choice = input("Choose RRR (Risk-Reward Ratio): [1:1], [1:2], or [1:3]: ").strip()
            if rrr_choice == "1:1":
                rrr_multiplier = 2  # 1:1 = 2×ATR for TP
                win_loss = 1  # Win $1 or lose $1
            elif rrr_choice == "1:2":
                rrr_multiplier = 4  # 1:2 = 4×ATR for TP
                win_loss = 2  # Win $2 or lose $1
            elif rrr_choice == "1:3":
                rrr_multiplier = 6  # 1:3 = 6×ATR for TP
                win_loss = 3  # Win $3 or lose $1
            else:
                print("Invalid RRR choice! Defaulting to 1:1.")
                rrr_multiplier = 2  # Default to 1:1 if invalid input
                win_loss = 1  # Default win/loss for 1:1

            # Calculate TP for both BUY and SELL actions based on selected RRR
            buy_tp = round_to_4_decimals(current_price + rrr_multiplier * atr)
            buy_sl = round_to_4_decimals(current_price - 2 * atr)  # SL stays 2×ATR for simplicity
            sell_tp = round_to_4_decimals(current_price - rrr_multiplier * atr)
            sell_sl = round_to_4_decimals(current_price + 2 * atr)  # SL stays 2×ATR for simplicity

            print(f"Trade action: {action} | TP: {buy_tp if action == 'B' else sell_tp} | SL: {buy_sl if action == 'B' else sell_sl}")  # Show TP and SL for the chosen action
            trade_action = "BUY" if action == "B" else "SELL"
            result, next_index = check_outcome(data, i, trade_action, buy_tp if trade_action == "BUY" else sell_tp, buy_sl if trade_action == "BUY" else sell_sl)

            if result == "TP":
                balance += win_loss
                score += 1
                consecutive_wins += 1
                print(f"Congrats! {trade_action} hit TP. +${win_loss}!")
            elif result == "SL":
                balance -= 1
                score -= 2  # Deduct 2 for a loss
                consecutive_wins = 0  # Reset streak
                print(f"Ouch! {trade_action} hit SL. -$1!")
            else:
                print(f"No TP or SL hit. No change in balance.")

            # Check for bonus after 2 wins in a row
            if consecutive_wins == 2:
                score += 3  # Bonus for 2 wins in a row
                print("Bonus! +3 points for 2 trades won in a row!")
                consecutive_wins = 0  # Reset streak

            print(f"Current Balance: ${balance} | Score: {score}")
            if balance <= 0:
                print("\nYou're broke! Game Over.")
                break

            # Track the raise amount
            raise_amount = balance - 100  # Calculate the raise amount

            # Check if balance falls below $80
            if balance <= 80:
                print("\nYour balance reached $80! Game Over.")
                break

            # Check if 5760 rows have passed and if the raise is less than $12 after each batch
            if i >= row_threshold * batch:
                if raise_amount < 12:
                    print(f"\nYou did not raise at least $12 after {5760 * batch} rows! Game Over.")
                    break
                batch += 1  # Move to the next batch

            # Track profit after 2880 rows
            if i >= 2880:
                profit_2880 = balance - start_balance  # Calculate profit after 2880 rows
                if profit_2880 >= 12:  # If profit is at least $12
                    score += 30  # Add the 30-point bonus
                    print(f"Bonus! +30 points for reaching $12 in profit after 2880 rows!")
                start_balance = balance  # Reset the starting balance for the next tracking period

            # Skip to the row where TP/SL resolved
            i = next_index
        elif action == "P":
            print("You passed this round. No change in balance.")
        else:
            print("Invalid choice! Skipping this round.")
        
        i += 1  # Move to the next row after the current one

    if balance > 0:
        print("\n🎮 Game Over!")
        print(f"Final Balance: ${balance} | Final Score: {score}")
    print("Thanks for playing. Better luck next time (or maybe you're ready for the big leagues)!")

# Load CSV and start game
file_name = "audusd-h1-bid-2003-08-03T21-2024-05-27.csv"  # Replace with your CSV file path
try:
    forex_data = load_data(file_name)
    forex_game(forex_data)
except FileNotFoundError:
    print("Error: The specified CSV file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
