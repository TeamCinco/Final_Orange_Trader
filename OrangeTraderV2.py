import csv
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any
from tqdm import tqdm

#### UI improvements
from colorama import init, Fore, Back, Style
init()  # Initialize colorama

class UIFormatter:
    @staticmethod
    def format_price(price: float) -> str:
        return f"{Fore.YELLOW}{price:.4f}{Style.RESET_ALL}"
    
    @staticmethod
    def format_balance(balance: float) -> str:
        color = Fore.GREEN if balance >= 100 else Fore.RED
        return f"{color}${balance:.2f}{Style.RESET_ALL}"
    
    @staticmethod
    def format_indicator(value: float) -> str:
        return f"{Fore.CYAN}{value:.6f}{Style.RESET_ALL}"
    
    @staticmethod
    def format_header(text: str) -> str:
        return f"\n{Fore.WHITE}{Back.BLUE}{text}{Style.RESET_ALL}"
    
def display_state(self, current_data: Dict):
        print("\n" + "=" * 80)
        print(f"{Fore.WHITE}{Back.BLUE} MARKET DATA {Style.RESET_ALL}")
        print(f"""
📅 Time: {Fore.YELLOW}{current_data['Time']}{Style.RESET_ALL}
💰 Balance: {self.ui.format_balance(self.state.balance)} | 🎯 Score: {Fore.CYAN}{self.state.score}{Style.RESET_ALL}
📊 Price: {self.ui.format_price(current_data['Price'])} | ATR: {self.ui.format_indicator(current_data['ATR'])}

{Fore.WHITE}Technical Indicators:{Style.RESET_ALL}
┌──────────────────────────────────────────┐
│ LWPI: {self.ui.format_indicator(current_data['LWPI'])}
│ ALMA: {self.ui.format_indicator(current_data['ALMA'])}
│ VIX:  {self.ui.format_indicator(current_data['VIX'])}
└──────────────────────────────────────────┘

{Fore.WHITE}Momentum Indicators:{Style.RESET_ALL}
┌──────────────────────────────────────────┐
│ Stochastic: {self.ui.format_indicator(current_data['Filt_Stoch'])}
│ Signal:     {self.ui.format_indicator(current_data['Sig'])}
│ ATR EMA:    {self.ui.format_indicator(current_data['ATR_EMA'])}
└──────────────────────────────────────────┘
""")
        


def get_trade_input(self) -> Tuple[str, str]:
        print(f"\n{Fore.GREEN}Available Actions:{Style.RESET_ALL}")
        print("1. Buy")
        print("2. Sell")
        print("3. Pass")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Enter your choice (1-3):{Style.RESET_ALL} ")
                if choice == "1":
                    action = "B"
                elif choice == "2":
                    action = "S"
                elif choice == "3":
                    return "P", "1:1"
                else:
                    print(f"{Fore.RED}Invalid choice! Please enter 1, 2, or 3.{Style.RESET_ALL}")
                    continue
                
                print(f"\n{Fore.GREEN}Risk-Reward Ratio Options:{Style.RESET_ALL}")
                print("1. 1:1 - Conservative")
                print("2. 1:2 - Balanced")
                print("3. 1:3 - Aggressive")
                
                rrr = input(f"\n{Fore.YELLOW}Enter RRR choice (1-3):{Style.RESET_ALL} ")
                if rrr == "1":
                    return action, "1:1"
                elif rrr == "2":
                    return action, "1:2"
                elif rrr == "3":
                    return action, "1:3"
                else:
                    print(f"{Fore.RED}Invalid RRR! Defaulting to 1:1.{Style.RESET_ALL}")
                    return action, "1:1"
                
            except ValueError:
                print(f"{Fore.RED}Invalid input! Please try again.{Style.RESET_ALL}")



def display_trade_result(self, result: str, trade_action: str, win_amount: float, reward: float):
        if result == "TP":
            print(f"\n{Fore.GREEN}🎯 TAKE PROFIT HIT!{Style.RESET_ALL}")
            print(f"Trade: {trade_action} | Profit: +${win_amount}")
        elif result == "SL":
            print(f"\n{Fore.RED}⚠️ STOP LOSS HIT!{Style.RESET_ALL}")
            print(f"Trade: {trade_action} | Loss: -$1")
        
        print(f"\n{Fore.CYAN}Trade Statistics:{Style.RESET_ALL}")
        print(f"Reward Points: {reward:+.2f}")
        print(f"Consecutive Wins: {self.state.consecutive_wins}")
        print(f"Current Drawdown: {self.state.drawdown:.2%}")

# actual code 
@dataclass
class TradeSettings:
    rrr_multipliers = {
        "1:1": (2, 1),  # (multiplier, win_amount)
        "1:2": (4, 2),
        "1:3": (6, 3)
    }
    default_sl_multiplier = 2
    starting_balance = 100
    min_balance = 80
    required_raise = 12
    batch_size = 5760
    profit_check_interval = 2880

class ForexDataHandler:
    def __init__(self, file_name: str):
        self.data = self.load_data(file_name)
        
    @staticmethod
    def load_data(file_name: str) -> List[Dict]:
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

class TradeCalculator:
    @staticmethod
    def round_to_4_decimals(value: float) -> float:
        return round(value, 4)

    @staticmethod
    def calculate_trade_levels(price: float, atr: float, rrr_multiplier: float) -> Tuple[float, float, float, float]:
        buy_tp = TradeCalculator.round_to_4_decimals(price + rrr_multiplier * atr)
        buy_sl = TradeCalculator.round_to_4_decimals(price - TradeSettings.default_sl_multiplier * atr)
        sell_tp = TradeCalculator.round_to_4_decimals(price - rrr_multiplier * atr)
        sell_sl = TradeCalculator.round_to_4_decimals(price + TradeSettings.default_sl_multiplier * atr)
        return buy_tp, buy_sl, sell_tp, sell_sl

    @staticmethod
    def check_outcome(data: List[Dict], start_index: int, trade_action: str, tp: float, sl: float) -> Tuple[str, int]:
        entry_price = data[start_index]["Price"]
        for i in range(start_index + 1, len(data)):
            current_price = data[i]["Price"]
            if (trade_action == "BUY" and current_price >= tp) or (trade_action == "SELL" and current_price <= tp):
                return "TP", i
            if (trade_action == "BUY" and current_price <= sl) or (trade_action == "SELL" and current_price >= sl):
                return "SL", i
        return "No TP or SL", len(data) - 1

class GameState:
    def __init__(self):
        self.balance = TradeSettings.starting_balance
        self.score = 0
        self.consecutive_wins = 0
        self.raise_amount = 0
        self.batch = 1
        self.profit_2880 = 0
        self.start_balance = TradeSettings.starting_balance
        self.reward_calculator = TradingRewardCalculator(TradeSettings.starting_balance)
        self.drawdown = 0
        self.peak_balance = TradeSettings.starting_balance

    def update_balance(self, amount: float):
        self.balance += amount
        self.raise_amount = self.balance - TradeSettings.starting_balance
        
        # Update peak balance and drawdown
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance
        self.drawdown = (self.peak_balance - self.balance) / self.peak_balance if self.peak_balance > 0 else 0

    def check_game_over(self, current_row: int) -> Tuple[bool, str]:
        if self.balance <= 0:
            return True, "You're broke!"
        if self.balance <= TradeSettings.min_balance:
            return True, f"Your balance reached ${TradeSettings.min_balance}!"
        if current_row >= TradeSettings.batch_size * self.batch and self.raise_amount < TradeSettings.required_raise:
            return True, f"You did not raise at least ${TradeSettings.required_raise} after {TradeSettings.batch_size * self.batch} rows!"
        return False, ""

    def calculate_trade_reward(self, trade_result, risk_to_reward, high_risk_setup=False):
        reward = self.reward_calculator.calculate_reward(
            trade_result=trade_result,
            current_balance=self.balance,
            risk_to_reward=risk_to_reward,
            streaks=self.consecutive_wins,
            high_risk_setup=high_risk_setup,
            drawdown=self.drawdown
        )
        self.reward_calculator.update_state(
            self.balance,
            risk_to_reward,
            self.consecutive_wins,
            self.drawdown
        )
        return reward

class ForexGame:
    def __init__(self, data_handler: ForexDataHandler):
        self.data = data_handler.data
        self.state = GameState()
        self.calculator = TradeCalculator()
        self.ui = UIFormatter()  # Keep the UI formatter

    def display_state(self, current_data: Dict):
        print("\n" + "=" * 80)
        print(f"{Fore.WHITE}{Back.BLUE} MARKET DATA {Style.RESET_ALL}")
        print(f"""
📅 Time: {Fore.YELLOW}{current_data['Time']}{Style.RESET_ALL}
💰 Balance: {self.ui.format_balance(self.state.balance)} | 🎯 Score: {Fore.CYAN}{self.state.score}{Style.RESET_ALL}
📊 Price: {self.ui.format_price(current_data['Price'])} | ATR: {self.ui.format_indicator(current_data['ATR'])}

{Fore.WHITE}Technical Indicators:{Style.RESET_ALL}
┌──────────────────────────────────────────┐
│ LWPI: {self.ui.format_indicator(current_data['LWPI'])}
│ ALMA: {self.ui.format_indicator(current_data['ALMA'])}
│ VIX:  {self.ui.format_indicator(current_data['VIX'])}
└──────────────────────────────────────────┘

{Fore.WHITE}Momentum Indicators:{Style.RESET_ALL}
┌──────────────────────────────────────────┐
│ Stochastic: {self.ui.format_indicator(current_data['Filt_Stoch'])}
│ Signal:     {self.ui.format_indicator(current_data['Sig'])}
│ ATR EMA:    {self.ui.format_indicator(current_data['ATR_EMA'])}
└──────────────────────────────────────────┘
""")

    def get_trade_input(self) -> Tuple[str, str]:
        print(f"\n{Fore.GREEN}Available Actions:{Style.RESET_ALL}")
        print("1. Buy")
        print("2. Sell")
        print("3. Pass")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Enter your choice (1-3):{Style.RESET_ALL} ")
                if choice == "1":
                    action = "B"
                elif choice == "2":
                    action = "S"
                elif choice == "3":
                    return "P", "1:1"
                else:
                    print(f"{Fore.RED}Invalid choice! Please enter 1, 2, or 3.{Style.RESET_ALL}")
                    continue
                
                print(f"\n{Fore.GREEN}Risk-Reward Ratio Options:{Style.RESET_ALL}")
                print("1. 1:1 - Conservative")
                print("2. 1:2 - Balanced")
                print("3. 1:3 - Aggressive")
                
                rrr = input(f"\n{Fore.YELLOW}Enter RRR choice (1-3):{Style.RESET_ALL} ")
                if rrr == "1":
                    return action, "1:1"
                elif rrr == "2":
                    return action, "1:2"
                elif rrr == "3":
                    return action, "1:3"
                else:
                    print(f"{Fore.RED}Invalid RRR! Defaulting to 1:1.{Style.RESET_ALL}")
                    return action, "1:1"
                
            except ValueError:
                print(f"{Fore.RED}Invalid input! Please try again.{Style.RESET_ALL}")

    def run(self):
        print(f"{Fore.GREEN}Welcome to the Forex Trading Simulator!{Style.RESET_ALL}")
        print("=" * 50)
        print(f"{Fore.YELLOW}Rules:{Style.RESET_ALL}")
        print("• TP and SL are based on ATR (Average True Range)")
        print("• Bonus points for consecutive wins")
        print("• Watch your drawdown!")
        print("=" * 50)
        
        with tqdm(total=len(self.data), desc="Trading Progress", ncols=80) as pbar:
            i = 0
            while i < len(self.data) - 1:
                current_data = self.data[i]
                
                if current_data["ATR"] == 0:
                    print(f"\nWarning: ATR is 0 at time {current_data['Time']}. Skipping this row.")
                    i += 1
                    pbar.update(1)
                    continue

                self.display_state(current_data)
                action, rrr_choice = self.get_trade_input()

                if action in ["B", "S"]:
                    next_index = self.process_trade(action, rrr_choice, current_data, i)
                    i = next_index
                    pbar.update(next_index - i + 1)
                else:
                    print("You passed this round. No change in balance.")
                    i += 1
                    pbar.update(1)

                game_over, message = self.state.check_game_over(i)
                if game_over:
                    print(f"\n{message}")
                    break

        self.end_game()

    def process_trade(self, action: str, rrr_choice: str, current_data: Dict, current_index: int):
        rrr_multiplier, win_amount = TradeSettings.rrr_multipliers[rrr_choice]
        buy_tp, buy_sl, sell_tp, sell_sl = self.calculator.calculate_trade_levels(
            current_data["Price"], current_data["ATR"], rrr_multiplier
        )

        trade_action = "BUY" if action == "B" else "SELL"
        tp = buy_tp if trade_action == "BUY" else sell_tp
        sl = buy_sl if trade_action == "BUY" else sell_sl

        print(f"Trade action: {action} | TP: {tp} | SL: {sl}")
        result, next_index = self.calculator.check_outcome(self.data, current_index, trade_action, tp, sl)

        # Calculate trade result as percentage of balance
        trade_result = 0
        if result == "TP":
            trade_result = (win_amount / self.state.balance) * 100
            self.state.update_balance(win_amount)
            self.state.consecutive_wins += 1
        elif result == "SL":
            trade_result = (-1 / self.state.balance) * 100
            self.state.update_balance(-1)
            self.state.consecutive_wins = 0

        # Calculate reward using new reward structure
        reward = self.state.calculate_trade_reward(
            trade_result=trade_result,
            risk_to_reward=rrr_multiplier/2,
            high_risk_setup=current_data["VIX"] > 20
        )
        
        self.state.score += reward
        self.display_trade_result(result, trade_action, win_amount if result == "TP" else -1, reward)
        
        return next_index

    def display_trade_result(self, result: str, trade_action: str, win_amount: float, reward: float):
        if result == "TP":
            print(f"\n{Fore.GREEN}🎯 TAKE PROFIT HIT!{Style.RESET_ALL}")
            print(f"Trade: {trade_action} | Profit: +${win_amount}")
        elif result == "SL":
            print(f"\n{Fore.RED}⚠️ STOP LOSS HIT!{Style.RESET_ALL}")
            print(f"Trade: {trade_action} | Loss: -$1")
        
        print(f"\n{Fore.CYAN}Trade Statistics:{Style.RESET_ALL}")
        print(f"Reward Points: {reward:+.2f}")
        print(f"Consecutive Wins: {self.state.consecutive_wins}")
        print(f"Current Drawdown: {self.state.drawdown:.2%}")

    def end_game(self):
        print("\n" + "=" * 80)
        if self.state.balance > 0:
            print(f"{Fore.GREEN}🎮 Game Over!{Style.RESET_ALL}")
            print(f"""
Final Statistics:
----------------
Balance: {self.ui.format_balance(self.state.balance)}
Score: {Fore.CYAN}{self.state.score}{Style.RESET_ALL}
Max Drawdown: {Fore.RED}{self.state.drawdown:.2%}{Style.RESET_ALL}
Total Trades: {self.state.reward_calculator.row_counter}
            """)
        print(f"{Fore.YELLOW}Thanks for playing! Better luck next time!{Style.RESET_ALL}")
class TradingRewardCalculator:
    def __init__(self, initial_balance):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.previous_balance = initial_balance
        self.weekly_start_balance = initial_balance
        self.monthly_start_balance = initial_balance
        self.yearly_start_balance = initial_balance
        self.row_counter = 0
        self.streaks = 0
        self.drawdown = 0
        self.risk_to_reward = 0

    def calculate_reward(self, trade_result, current_balance, risk_to_reward, streaks, high_risk_setup, drawdown):
        reward = 0
        self.row_counter += 1

        # Immediate Outcomes
        if trade_result >= 0.02 * current_balance:
            reward += 1
        elif trade_result <= -0.02 * current_balance:
            reward -= 1

        # Risk-to-Reward Ratio
        if risk_to_reward > 2:
            reward += 2
        elif risk_to_reward < 1:
            reward -= 2

        # Streaks
        if streaks == 2:
            reward += 3
        elif streaks >= 3:
            reward += 5
        elif streaks <= -3:
            reward -= 3

        # High-Risk Setup
        if high_risk_setup:
            if risk_to_reward > 2:
                reward += 3
            else:
                reward -= 2

        # Periodic Performance Checks
        self._check_periodic_performance(current_balance, drawdown, reward)
        
        # Risk Management
        reward += self._calculate_risk_management_reward(current_balance, drawdown)

        return reward

    def _check_periodic_performance(self, current_balance, drawdown, reward):
        # Weekly Check (120 rows)
        if self.row_counter % 120 == 0:
            weekly_balance = current_balance - self.weekly_start_balance
            if weekly_balance > 0:
                reward += 5
            elif weekly_balance < 0:
                reward -= 3
            
            if drawdown > 0.10:
                reward -= 5
            elif drawdown < 0.05:
                reward += 3
                
            self.weekly_start_balance = current_balance

        # Monthly Check (480 rows)
        if self.row_counter % 480 == 0:
            monthly_balance = current_balance - self.monthly_start_balance
            if monthly_balance > 5:
                reward += 10
            elif monthly_balance < -5:
                reward -= 5
            elif monthly_balance < 0:
                reward += 2
                
            self.monthly_start_balance = current_balance

        # Yearly Check (5760 rows)
        if self.row_counter % 5760 == 0:
            yearly_balance = current_balance - self.yearly_start_balance
            if yearly_balance > 20:
                reward += 30
            elif yearly_balance < -10:
                reward -= 10
                
            self.yearly_start_balance = current_balance

    def _calculate_risk_management_reward(self, current_balance, drawdown):
        reward = 0
        if drawdown > 0.10:
            reward -= 10
        elif drawdown > 0.50:
            reward -= 50

        if drawdown >= 0.20 and current_balance > self.previous_balance * 1.10:
            reward += 20
        elif drawdown < 0.20:
            reward += 3

        if current_balance < self.previous_balance - 10:
            reward -= 5
        elif current_balance < self.previous_balance - 20:
            reward -= 10

        return reward

    def update_state(self, new_balance, risk_to_reward, streaks, drawdown):
        self.previous_balance = self.balance
        self.balance = new_balance
        self.risk_to_reward = risk_to_reward
        self.streaks = streaks
        self.drawdown = drawdown
def main():
    file_name = "audusd-h1-bid-2003-08-03T21-2024-05-27.csv"
    try:
        data_handler = ForexDataHandler(file_name)
        game = ForexGame(data_handler)
        game.run()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: The specified CSV file was not found.{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Game interrupted by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()