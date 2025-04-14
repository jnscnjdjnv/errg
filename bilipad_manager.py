#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import json
import random
import requests
import datetime
<<<<<<< HEAD
import csv
import re
import shutil
=======
>>>>>>> e7354fb9863b184dadd86cf14240a7ae60918c0e
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the program banner"""
    banner = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗
███████  █████  ██    ██  █████  ███    ██ 
██      ██   ██ ██    ██ ██   ██ ████   ██ 
███████ ███████ ██    ██ ███████ ██ ██  ██ 
     ██ ██   ██  ██  ██  ██   ██ ██  ██ ██ 
███████ ██   ██   ████   ██   ██ ██   ████ 
║                                                                                ║
║  Telegram: @savanop121                                                        ║
║  GitHub: https://github.com/jnscnjdjnv/billipad.git                           ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def add_proxy():
    """Add a proxy to proxies.txt"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Adding Proxy{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Enter proxy in format: username:password@host:port or host:port{Style.RESET_ALL}")
    proxy = input(f"{Fore.GREEN}Proxy: {Style.RESET_ALL}")
    
    if not proxy:
        print(f"{Fore.RED}[!] Proxy cannot be empty{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        with open("proxies.txt", "a") as f:
            f.write(proxy + "\n")
        print(f"{Fore.GREEN}[+] Proxy added successfully{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error adding proxy: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def delete_proxies():
    """Delete all proxies from proxies.txt"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Deleting All Proxies{Style.RESET_ALL}")
    
    confirm = input(f"{Fore.RED}Are you sure you want to delete all proxies? (y/n): {Style.RESET_ALL}")
    
    if confirm.lower() == 'y':
        try:
            with open("proxies.txt", "w") as f:
                f.write("")
            print(f"{Fore.GREEN}[+] All proxies deleted successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error deleting proxies: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def add_referral_code():
    """Add a referral code to referral_code.txt"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Adding Referral Code{Style.RESET_ALL}")
    
    referral_code = input(f"{Fore.GREEN}Enter referral code: {Style.RESET_ALL}")
    
    if not referral_code:
        print(f"{Fore.RED}[!] Referral code cannot be empty{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        with open("referral_code.txt", "w") as f:
            f.write(referral_code)
        print(f"{Fore.GREEN}[+] Referral code added successfully{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error adding referral code: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def delete_referral_code():
    """Delete referral code from referral_code.txt"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Deleting Referral Code{Style.RESET_ALL}")
    
    confirm = input(f"{Fore.RED}Are you sure you want to delete the referral code? (y/n): {Style.RESET_ALL}")
    
    if confirm.lower() == 'y':
        try:
            with open("referral_code.txt", "w") as f:
                f.write("")
            print(f"{Fore.GREEN}[+] Referral code deleted successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error deleting referral code: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def start_account_creation():
    """Start the account creation process"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Starting Account Creation{Style.RESET_ALL}")
    
    # Check if referral code exists
    try:
        with open("referral_code.txt", "r") as f:
            referral_code = f.read().strip()
            if not referral_code:
                print(f"{Fore.RED}[!] No referral code found. Please add a referral code first.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
    except FileNotFoundError:
        print(f"{Fore.RED}[!] referral_code.txt not found. Please add a referral code first.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    # Check if proxies exist
    try:
        with open("proxies.txt", "r") as f:
            proxies = f.readlines()
            if not proxies:
                print(f"{Fore.YELLOW}[!] No proxies found. The script will run without proxies.{Style.RESET_ALL}")
                confirm = input(f"{Fore.YELLOW}Do you want to continue without proxies? (y/n): {Style.RESET_ALL}")
                if confirm.lower() != 'y':
                    print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] proxies.txt not found. The script will run without proxies.{Style.RESET_ALL}")
        confirm = input(f"{Fore.YELLOW}Do you want to continue without proxies? (y/n): {Style.RESET_ALL}")
        if confirm.lower() != 'y':
            print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
    
    # Get number of accounts to create
    try:
        num_accounts = int(input(f"{Fore.GREEN}Enter number of accounts to create: {Style.RESET_ALL}"))
        if num_accounts <= 0:
            print(f"{Fore.RED}[!] Number of accounts must be greater than 0{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
    except ValueError:
        print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    # Run the main script
    print(f"{Fore.GREEN}[+] Starting account creation for {num_accounts} accounts...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop the process{Style.RESET_ALL}")
    
    try:
        # Create a temporary file with the number of accounts
        with open("num_accounts.txt", "w") as f:
            f.write(str(num_accounts))
        
        # Run the main script
        subprocess.run([sys.executable, "bilipad_ref_auto_insiders.py"])
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}[*] Process interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error running script: {str(e)}{Style.RESET_ALL}")
    finally:
        # Clean up temporary file
        if os.path.exists("num_accounts.txt"):
            os.remove("num_accounts.txt")
        
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def view_accounts():
    """View all created accounts"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Viewing Accounts{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Found {len(accounts)} accounts:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Tasks{Fore.CYAN}  |  {Fore.YELLOW}Wallet{Fore.CYAN}  |  {Fore.YELLOW}Created{Fore.CYAN}  ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        
        for i, account in enumerate(accounts):
            email = account.get("email", "N/A")
            tasks = account.get("tasksCompleted", 0)
            wallet = account.get("wallet", {}).get("address", "N/A")
            if wallet != "N/A":
                wallet = wallet[:6] + "..." + wallet[-4:]
            created = account.get("createdAt", "N/A")
            if created != "N/A":
                try:
                    created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                    created = created_date.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{tasks}/7{Fore.CYAN}  |  {Fore.WHITE}{wallet}{Fore.CYAN}  |  {Fore.WHITE}{created}{Fore.CYAN}  ║")
        
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Ask if user wants to export accounts
        export = input(f"{Fore.YELLOW}Do you want to export accounts to CSV? (y/n): {Style.RESET_ALL}")
        if export.lower() == 'y':
            export_accounts_to_csv(accounts)
    except Exception as e:
        print(f"{Fore.RED}[!] Error viewing accounts: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def export_accounts_to_csv(accounts):
    """Export accounts to CSV file"""
    try:
<<<<<<< HEAD
=======
        import csv
>>>>>>> e7354fb9863b184dadd86cf14240a7ae60918c0e
        from datetime import datetime
        
        filename = f"bilipad_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['email', 'password', 'userId', 'deviceId', 'authToken', 'wallet_address', 'wallet_privateKey', 'createdAt', 'proxy', 'tasksCompleted']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for account in accounts:
                row = {
                    'email': account.get('email', ''),
                    'password': account.get('password', ''),
                    'userId': account.get('userId', ''),
                    'deviceId': account.get('deviceId', ''),
                    'authToken': account.get('authToken', ''),
                    'wallet_address': account.get('wallet', {}).get('address', ''),
                    'wallet_privateKey': account.get('wallet', {}).get('privateKey', ''),
                    'createdAt': account.get('createdAt', ''),
                    'proxy': account.get('proxy', ''),
                    'tasksCompleted': account.get('tasksCompleted', 0)
                }
                writer.writerow(row)
        
        print(f"{Fore.GREEN}[+] Accounts exported to {filename}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error exporting accounts: {str(e)}{Style.RESET_ALL}")

def test_proxies():
    """Test all proxies for connectivity"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Testing Proxies{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("proxies.txt"):
            print(f"{Fore.RED}[!] No proxies found. Please add proxies first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        if not proxies:
            print(f"{Fore.RED}[!] No proxies found. Please add proxies first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Found {len(proxies)} proxies. Testing...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Proxy{Fore.CYAN}  |  {Fore.YELLOW}Status{Fore.CYAN}  |  {Fore.YELLOW}Response Time{Fore.CYAN}  ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        
        working_proxies = []
        for i, proxy in enumerate(proxies):
            print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{proxy}{Fore.CYAN}  |  {Fore.YELLOW}Testing...{Fore.CYAN}  |  {Fore.WHITE}...{Fore.CYAN}  ║")
            
            try:
                start_time = time.time()
                proxies_dict = {
                    'http': f"http://{proxy}",
                    'https': f"http://{proxy}"
                }
                
                response = requests.get("https://billipad.finance", proxies=proxies_dict, timeout=10, verify=False)
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000)
                
                if response.status_code == 200:
                    status = f"{Fore.GREEN}OK{Style.RESET_ALL}"
                    working_proxies.append(proxy)
                else:
                    status = f"{Fore.RED}Error ({response.status_code}){Style.RESET_ALL}"
                
                # Clear the previous line and print the result
                print(f"\033[F\033[K║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{proxy}{Fore.CYAN}  |  {status}  |  {Fore.WHITE}{response_time}ms{Fore.CYAN}  ║")
            except Exception as e:
                # Clear the previous line and print the error
                print(f"\033[F\033[K║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{proxy}{Fore.CYAN}  |  {Fore.RED}Failed{Style.RESET_ALL}  |  {Fore.WHITE}N/A{Fore.CYAN}  ║")
        
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Found {len(working_proxies)} working proxies out of {len(proxies)}{Style.RESET_ALL}")
        
        # Ask if user wants to save working proxies
        if working_proxies:
            save = input(f"{Fore.YELLOW}Do you want to save working proxies to a new file? (y/n): {Style.RESET_ALL}")
            if save.lower() == 'y':
                filename = f"working_proxies_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, "w") as f:
                    for proxy in working_proxies:
                        f.write(proxy + "\n")
                print(f"{Fore.GREEN}[+] Working proxies saved to {filename}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error testing proxies: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def view_statistics():
    """View statistics about created accounts"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Account Statistics{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Calculate statistics
        total_accounts = len(accounts)
        completed_tasks = sum(1 for acc in accounts if acc.get("tasksCompleted", 0) == 7)
        partial_tasks = sum(1 for acc in accounts if 0 < acc.get("tasksCompleted", 0) < 7)
        no_tasks = sum(1 for acc in accounts if acc.get("tasksCompleted", 0) == 0)
        
        # Calculate average tasks completed
        avg_tasks = sum(acc.get("tasksCompleted", 0) for acc in accounts) / total_accounts
        
        # Calculate accounts by date
        accounts_by_date = {}
        for acc in accounts:
            created = acc.get("createdAt", "")
            if created:
                try:
                    date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                    if date in accounts_by_date:
                        accounts_by_date[date] += 1
                    else:
                        accounts_by_date[date] = 1
                except:
                    pass
        
        # Print statistics
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  {Fore.YELLOW}Total Accounts:{Fore.CYAN} {Fore.WHITE}{total_accounts}{Fore.CYAN}                                                      ║")
        print(f"║  {Fore.YELLOW}Completed Tasks:{Fore.CYAN} {Fore.WHITE}{completed_tasks}{Fore.CYAN} ({Fore.WHITE}{round(completed_tasks/total_accounts*100 if total_accounts > 0 else 0, 1)}{Fore.CYAN}%)                                                  ║")
        print(f"║  {Fore.YELLOW}Partial Tasks:{Fore.CYAN} {Fore.WHITE}{partial_tasks}{Fore.CYAN} ({Fore.WHITE}{round(partial_tasks/total_accounts*100 if total_accounts > 0 else 0, 1)}{Fore.CYAN}%)                                                    ║")
        print(f"║  {Fore.YELLOW}No Tasks:{Fore.CYAN} {Fore.WHITE}{no_tasks}{Fore.CYAN} ({Fore.WHITE}{round(no_tasks/total_accounts*100 if total_accounts > 0 else 0, 1)}{Fore.CYAN}%)                                                        ║")
        print(f"║  {Fore.YELLOW}Average Tasks:{Fore.CYAN} {Fore.WHITE}{round(avg_tasks, 1)}{Fore.CYAN}/7                                                      ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        print(f"║  {Fore.YELLOW}Accounts by Date:{Fore.CYAN}                                                              ║")
        
        for date, count in sorted(accounts_by_date.items()):
            print(f"║  {Fore.WHITE}{date}{Fore.CYAN}: {Fore.GREEN}{count}{Fore.CYAN} accounts                                                      ║")
        
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error viewing statistics: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def delete_accounts():
    """Delete all accounts from accounts.json"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Deleting All Accounts{Style.RESET_ALL}")
    
    confirm = input(f"{Fore.RED}Are you sure you want to delete all accounts? (y/n): {Style.RESET_ALL}")
    
    if confirm.lower() == 'y':
        try:
            with open("accounts.json", "w") as f:
                json.dump([], f)
            print(f"{Fore.GREEN}[+] All accounts deleted successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error deleting accounts: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def backup_accounts():
    """Create a backup of accounts.json"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Backing Up Accounts{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Create backup directory if it doesn't exist
        if not os.path.exists("backups"):
            os.makedirs("backups")
        
        # Create backup file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/accounts_backup_{timestamp}.json"
        
        # Copy accounts.json to backup file
        with open("accounts.json", "r") as src, open(backup_file, "w") as dst:
            dst.write(src.read())
        
        print(f"{Fore.GREEN}[+] Accounts backed up to {backup_file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error backing up accounts: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def restore_accounts():
    """Restore accounts from a backup"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Restoring Accounts{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("backups"):
            print(f"{Fore.RED}[!] No backups found. Please create a backup first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        backup_files = [f for f in os.listdir("backups") if f.startswith("accounts_backup_") and f.endswith(".json")]
        
        if not backup_files:
            print(f"{Fore.RED}[!] No backups found. Please create a backup first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Sort backup files by date (newest first)
        backup_files.sort(reverse=True)
        
        print(f"{Fore.GREEN}[+] Found {len(backup_files)} backups:{Style.RESET_ALL}")
        for i, file in enumerate(backup_files):
            print(f"{Fore.CYAN}[{Fore.GREEN}{i+1}{Fore.CYAN}] {Fore.WHITE}{file}{Style.RESET_ALL}")
        
        choice = input(f"{Fore.YELLOW}Enter backup number to restore (0 to cancel): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            if choice == 0:
                print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            if choice < 1 or choice > len(backup_files):
                print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            backup_file = backup_files[choice-1]
            backup_path = os.path.join("backups", backup_file)
            
            # Copy backup file to accounts.json
            with open(backup_path, "r") as src, open("accounts.json", "w") as dst:
                dst.write(src.read())
            
            print(f"{Fore.GREEN}[+] Accounts restored from {backup_file}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error restoring accounts: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

<<<<<<< HEAD
def import_proxies():
    """Import proxies from a file"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Importing Proxies{Style.RESET_ALL}")
    
    file_path = input(f"{Fore.GREEN}Enter the path to the proxy file: {Style.RESET_ALL}")
    
    if not os.path.exists(file_path):
        print(f"{Fore.RED}[!] File not found: {file_path}{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        with open(file_path, "r") as src, open("proxies.txt", "a") as dst:
            for line in src:
                if line.strip():
                    dst.write(line)
        
        # Count the number of proxies added
        with open("proxies.txt", "r") as f:
            proxy_count = sum(1 for line in f if line.strip())
        
        print(f"{Fore.GREEN}[+] Proxies imported successfully. Total proxies: {proxy_count}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error importing proxies: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def export_proxies():
    """Export proxies to a file"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Exporting Proxies{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("proxies.txt"):
            print(f"{Fore.RED}[!] No proxies found. Please add proxies first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        if not proxies:
            print(f"{Fore.RED}[!] No proxies found. Please add proxies first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Create export directory if it doesn't exist
        if not os.path.exists("exports"):
            os.makedirs("exports")
        
        # Create export file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"exports/proxies_export_{timestamp}.txt"
        
        # Write proxies to export file
        with open(export_file, "w") as f:
            for proxy in proxies:
                f.write(proxy + "\n")
        
        print(f"{Fore.GREEN}[+] {len(proxies)} proxies exported to {export_file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error exporting proxies: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def rotate_proxies():
    """Rotate proxies by moving the first proxy to the end"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Rotating Proxies{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("proxies.txt"):
            print(f"{Fore.RED}[!] No proxies found. Please add proxies first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        if not proxies:
            print(f"{Fore.RED}[!] No proxies found. Please add proxies first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        if len(proxies) <= 1:
            print(f"{Fore.YELLOW}[!] Not enough proxies to rotate. Need at least 2 proxies.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Rotate proxies
        first_proxy = proxies.pop(0)
        proxies.append(first_proxy)
        
        # Write rotated proxies back to file
        with open("proxies.txt", "w") as f:
            for proxy in proxies:
                f.write(proxy + "\n")
        
        print(f"{Fore.GREEN}[+] Proxies rotated successfully. First proxy moved to the end.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}First proxy: {Fore.WHITE}{first_proxy}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error rotating proxies: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def search_accounts():
    """Search for accounts by various criteria"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Search Accounts{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Search by:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[1]{Fore.CYAN} Email{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[2]{Fore.CYAN} Wallet Address{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[3]{Fore.CYAN} Tasks Completed{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[4]{Fore.CYAN} Creation Date{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[5]{Fore.CYAN} Proxy{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[0]{Fore.CYAN} Cancel{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '0':
            print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        search_term = input(f"{Fore.GREEN}Enter search term: {Style.RESET_ALL}")
        
        if not search_term:
            print(f"{Fore.RED}[!] Search term cannot be empty{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        results = []
        
        if choice == '1':
            # Search by email
            results = [acc for acc in accounts if search_term.lower() in acc.get("email", "").lower()]
        elif choice == '2':
            # Search by wallet address
            results = [acc for acc in accounts if search_term.lower() in acc.get("wallet", {}).get("address", "").lower()]
        elif choice == '3':
            # Search by tasks completed
            try:
                tasks = int(search_term)
                results = [acc for acc in accounts if acc.get("tasksCompleted", 0) == tasks]
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
        elif choice == '4':
            # Search by creation date
            results = [acc for acc in accounts if search_term in acc.get("createdAt", "")]
        elif choice == '5':
            # Search by proxy
            results = [acc for acc in accounts if search_term.lower() in str(acc.get("proxy", "")).lower()]
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        if not results:
            print(f"{Fore.YELLOW}[!] No accounts found matching your search criteria{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Found {len(results)} accounts matching your search criteria:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Tasks{Fore.CYAN}  |  {Fore.YELLOW}Wallet{Fore.CYAN}  |  {Fore.YELLOW}Created{Fore.CYAN}  ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        
        for i, account in enumerate(results):
            email = account.get("email", "N/A")
            tasks = account.get("tasksCompleted", 0)
            wallet = account.get("wallet", {}).get("address", "N/A")
            if wallet != "N/A":
                wallet = wallet[:6] + "..." + wallet[-4:]
            created = account.get("createdAt", "N/A")
            if created != "N/A":
                try:
                    created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                    created = created_date.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{tasks}/7{Fore.CYAN}  |  {Fore.WHITE}{wallet}{Fore.CYAN}  |  {Fore.WHITE}{created}{Fore.CYAN}  ║")
        
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Ask if user wants to export results
        export = input(f"{Fore.YELLOW}Do you want to export these accounts to CSV? (y/n): {Style.RESET_ALL}")
        if export.lower() == 'y':
            export_accounts_to_csv(results)
    except Exception as e:
        print(f"{Fore.RED}[!] Error searching accounts: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def filter_accounts():
    """Filter accounts by various criteria"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Filter Accounts{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Filter by:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[1]{Fore.CYAN} Tasks Completed (Equal to){Style.RESET_ALL}")
        print(f"{Fore.GREEN}[2]{Fore.CYAN} Tasks Completed (Greater than){Style.RESET_ALL}")
        print(f"{Fore.GREEN}[3]{Fore.CYAN} Tasks Completed (Less than){Style.RESET_ALL}")
        print(f"{Fore.GREEN}[4]{Fore.CYAN} Creation Date (After){Style.RESET_ALL}")
        print(f"{Fore.GREEN}[5]{Fore.CYAN} Creation Date (Before){Style.RESET_ALL}")
        print(f"{Fore.GREEN}[6]{Fore.CYAN} Has Proxy{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[7]{Fore.CYAN} No Proxy{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[0]{Fore.CYAN} Cancel{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '0':
            print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        results = []
        
        if choice in ['1', '2', '3']:
            try:
                tasks = int(input(f"{Fore.GREEN}Enter number of tasks: {Style.RESET_ALL}"))
                
                if choice == '1':
                    # Equal to
                    results = [acc for acc in accounts if acc.get("tasksCompleted", 0) == tasks]
                elif choice == '2':
                    # Greater than
                    results = [acc for acc in accounts if acc.get("tasksCompleted", 0) > tasks]
                elif choice == '3':
                    # Less than
                    results = [acc for acc in accounts if acc.get("tasksCompleted", 0) < tasks]
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
        elif choice in ['4', '5']:
            date_str = input(f"{Fore.GREEN}Enter date (YYYY-MM-DD): {Style.RESET_ALL}")
            
            try:
                filter_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                
                if choice == '4':
                    # After date
                    results = [acc for acc in accounts if acc.get("createdAt", "") and datetime.datetime.strptime(acc.get("createdAt", ""), "%Y-%m-%dT%H:%M:%SZ") > filter_date]
                elif choice == '5':
                    # Before date
                    results = [acc for acc in accounts if acc.get("createdAt", "") and datetime.datetime.strptime(acc.get("createdAt", ""), "%Y-%m-%dT%H:%M:%SZ") < filter_date]
            except ValueError:
                print(f"{Fore.RED}[!] Invalid date format. Please use YYYY-MM-DD.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
        elif choice == '6':
            # Has proxy
            results = [acc for acc in accounts if acc.get("proxy")]
        elif choice == '7':
            # No proxy
            results = [acc for acc in accounts if not acc.get("proxy")]
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        if not results:
            print(f"{Fore.YELLOW}[!] No accounts found matching your filter criteria{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Found {len(results)} accounts matching your filter criteria:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Tasks{Fore.CYAN}  |  {Fore.YELLOW}Wallet{Fore.CYAN}  |  {Fore.YELLOW}Created{Fore.CYAN}  ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        
        for i, account in enumerate(results):
            email = account.get("email", "N/A")
            tasks = account.get("tasksCompleted", 0)
            wallet = account.get("wallet", {}).get("address", "N/A")
            if wallet != "N/A":
                wallet = wallet[:6] + "..." + wallet[-4:]
            created = account.get("createdAt", "N/A")
            if created != "N/A":
                try:
                    created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                    created = created_date.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{tasks}/7{Fore.CYAN}  |  {Fore.WHITE}{wallet}{Fore.CYAN}  |  {Fore.WHITE}{created}{Fore.CYAN}  ║")
        
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Ask if user wants to export results
        export = input(f"{Fore.YELLOW}Do you want to export these accounts to CSV? (y/n): {Style.RESET_ALL}")
        if export.lower() == 'y':
            export_accounts_to_csv(results)
    except Exception as e:
        print(f"{Fore.RED}[!] Error filtering accounts: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def complete_tasks():
    """Complete tasks for selected accounts"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Complete Tasks{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Filter accounts with incomplete tasks
        incomplete_accounts = [acc for acc in accounts if acc.get("tasksCompleted", 0) < 7]
        
        if not incomplete_accounts:
            print(f"{Fore.GREEN}[+] All accounts have completed all tasks{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Found {len(incomplete_accounts)} accounts with incomplete tasks:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Tasks{Fore.CYAN}  |  {Fore.YELLOW}Wallet{Fore.CYAN}  |  {Fore.YELLOW}Created{Fore.CYAN}  ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        
        for i, account in enumerate(incomplete_accounts):
            email = account.get("email", "N/A")
            tasks = account.get("tasksCompleted", 0)
            wallet = account.get("wallet", {}).get("address", "N/A")
            if wallet != "N/A":
                wallet = wallet[:6] + "..." + wallet[-4:]
            created = account.get("createdAt", "N/A")
            if created != "N/A":
                try:
                    created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                    created = created_date.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{tasks}/7{Fore.CYAN}  |  {Fore.WHITE}{wallet}{Fore.CYAN}  |  {Fore.WHITE}{created}{Fore.CYAN}  ║")
        
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Ask user to select accounts
        print(f"{Fore.YELLOW}Enter account IDs to complete tasks for (comma-separated, e.g., 1,3,5 or 'all' for all accounts):{Style.RESET_ALL}")
        selection = input(f"{Fore.GREEN}Selection: {Style.RESET_ALL}")
        
        selected_accounts = []
        
        if selection.lower() == 'all':
            selected_accounts = incomplete_accounts
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                selected_accounts = [incomplete_accounts[idx] for idx in indices if 0 <= idx < len(incomplete_accounts)]
            except (ValueError, IndexError):
                print(f"{Fore.RED}[!] Invalid selection. Please enter valid account IDs.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
        
        if not selected_accounts:
            print(f"{Fore.RED}[!] No accounts selected{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Run the task completion script
        print(f"{Fore.GREEN}[+] Starting task completion for {len(selected_accounts)} accounts...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop the process{Style.RESET_ALL}")
        
        try:
            # Create a temporary file with the selected accounts
            with open("selected_accounts.json", "w") as f:
                json.dump(selected_accounts, f)
            
            # Run the task completion script
            subprocess.run([sys.executable, "bilipad_task_completion.py"])
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}[*] Process interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error running script: {str(e)}{Style.RESET_ALL}")
        finally:
            # Clean up temporary file
            if os.path.exists("selected_accounts.json"):
                os.remove("selected_accounts.json")
            
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error completing tasks: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def manage_wallets():
    """Manage wallet addresses for accounts"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Manage Wallets{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Wallet Management Options:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[1]{Fore.CYAN} View All Wallets{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[2]{Fore.CYAN} Update Wallet Address{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[3]{Fore.CYAN} Export Wallets to File{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[4]{Fore.CYAN} Import Wallets from File{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[0]{Fore.CYAN} Cancel{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '0':
            print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        if choice == '1':
            # View all wallets
            print(f"{Fore.GREEN}[+] Found {len(accounts)} accounts with wallets:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
            print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Wallet Address{Fore.CYAN}  |  {Fore.YELLOW}Private Key{Fore.CYAN}  ║")
            print(f"╠════════════════════════════════════════════════════════════════════════════╣")
            
            for i, account in enumerate(accounts):
                email = account.get("email", "N/A")
                wallet_address = account.get("wallet", {}).get("address", "N/A")
                private_key = account.get("wallet", {}).get("privateKey", "N/A")
                
                if wallet_address != "N/A":
                    wallet_address = wallet_address[:6] + "..." + wallet_address[-4:]
                if private_key != "N/A":
                    private_key = private_key[:6] + "..." + private_key[-4:]
                
                print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{wallet_address}{Fore.CYAN}  |  {Fore.WHITE}{private_key}{Fore.CYAN}  ║")
            
            print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        elif choice == '2':
            # Update wallet address
            print(f"{Fore.GREEN}[+] Found {len(accounts)} accounts:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
            print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Wallet Address{Fore.CYAN}  ║")
            print(f"╠════════════════════════════════════════════════════════════════════════════╣")
            
            for i, account in enumerate(accounts):
                email = account.get("email", "N/A")
                wallet_address = account.get("wallet", {}).get("address", "N/A")
                
                if wallet_address != "N/A":
                    wallet_address = wallet_address[:6] + "..." + wallet_address[-4:]
                
                print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{wallet_address}{Fore.CYAN}  ║")
            
            print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            account_id = input(f"{Fore.GREEN}Enter account ID to update: {Style.RESET_ALL}")
            
            try:
                account_id = int(account_id) - 1
                if account_id < 0 or account_id >= len(accounts):
                    print(f"{Fore.RED}[!] Invalid account ID{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                account = accounts[account_id]
                email = account.get("email", "N/A")
                
                print(f"{Fore.GREEN}[+] Updating wallet for account: {email}{Style.RESET_ALL}")
                
                wallet_address = input(f"{Fore.GREEN}Enter new wallet address: {Style.RESET_ALL}")
                private_key = input(f"{Fore.GREEN}Enter new private key: {Style.RESET_ALL}")
                
                if not wallet_address or not private_key:
                    print(f"{Fore.RED}[!] Wallet address and private key cannot be empty{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                # Update wallet
                if "wallet" not in account:
                    account["wallet"] = {}
                
                account["wallet"]["address"] = wallet_address
                account["wallet"]["privateKey"] = private_key
                
                # Save updated accounts
                with open("accounts.json", "w") as f:
                    json.dump(accounts, f, indent=2)
                
                print(f"{Fore.GREEN}[+] Wallet updated successfully{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
        elif choice == '3':
            # Export wallets to file
            # Create export directory if it doesn't exist
            if not os.path.exists("exports"):
                os.makedirs("exports")
            
            # Create export file with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"exports/wallets_export_{timestamp}.csv"
            
            with open(export_file, 'w', newline='') as csvfile:
                fieldnames = ['email', 'wallet_address', 'wallet_privateKey']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for account in accounts:
                    row = {
                        'email': account.get('email', ''),
                        'wallet_address': account.get('wallet', {}).get('address', ''),
                        'wallet_privateKey': account.get('wallet', {}).get('privateKey', '')
                    }
                    writer.writerow(row)
            
            print(f"{Fore.GREEN}[+] Wallets exported to {export_file}{Style.RESET_ALL}")
        elif choice == '4':
            # Import wallets from file
            file_path = input(f"{Fore.GREEN}Enter the path to the wallet file (CSV): {Style.RESET_ALL}")
            
            if not os.path.exists(file_path):
                print(f"{Fore.RED}[!] File not found: {file_path}{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            try:
                with open(file_path, 'r', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    for row in reader:
                        email = row.get('email', '')
                        wallet_address = row.get('wallet_address', '')
                        wallet_privateKey = row.get('wallet_privateKey', '')
                        
                        if not email or not wallet_address or not wallet_privateKey:
                            continue
                        
                        # Find account by email
                        for account in accounts:
                            if account.get('email', '') == email:
                                # Update wallet
                                if "wallet" not in account:
                                    account["wallet"] = {}
                                
                                account["wallet"]["address"] = wallet_address
                                account["wallet"]["privateKey"] = wallet_privateKey
                                break
                
                # Save updated accounts
                with open("accounts.json", "w") as f:
                    json.dump(accounts, f, indent=2)
                
                print(f"{Fore.GREEN}[+] Wallets imported successfully{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Error importing wallets: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error managing wallets: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def manage_account_groups():
    """Manage account groups and tags"""
    clear_screen()
    print_banner()
    print(f"{Fore.YELLOW}[*] Manage Account Groups{Style.RESET_ALL}")
    
    try:
        if not os.path.exists("accounts.json"):
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print(f"{Fore.RED}[!] No accounts found. Please create accounts first.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Check if groups file exists, create if not
        if not os.path.exists("account_groups.json"):
            with open("account_groups.json", "w") as f:
                json.dump({}, f)
        
        with open("account_groups.json", "r") as f:
            groups = json.load(f)
        
        print(f"{Fore.CYAN}Group Management Options:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[1]{Fore.CYAN} View All Groups{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[2]{Fore.CYAN} Create New Group{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[3]{Fore.CYAN} Add Account to Group{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[4]{Fore.CYAN} Remove Account from Group{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[5]{Fore.CYAN} Delete Group{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[6]{Fore.CYAN} View Accounts in Group{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[0]{Fore.CYAN} Cancel{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '0':
            print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        if choice == '1':
            # View all groups
            if not groups:
                print(f"{Fore.YELLOW}[!] No groups found. Please create a group first.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}[+] Found {len(groups)} groups:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
            print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Group Name{Fore.CYAN}  |  {Fore.YELLOW}Account Count{Fore.CYAN}  ║")
            print(f"╠════════════════════════════════════════════════════════════════════════════╣")
            
            for i, (group_name, group_data) in enumerate(groups.items()):
                account_count = len(group_data.get("accounts", []))
                print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{group_name}{Fore.CYAN}  |  {Fore.WHITE}{account_count}{Fore.CYAN}  ║")
            
            print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        elif choice == '2':
            # Create new group
            group_name = input(f"{Fore.GREEN}Enter group name: {Style.RESET_ALL}")
            
            if not group_name:
                print(f"{Fore.RED}[!] Group name cannot be empty{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            if group_name in groups:
                print(f"{Fore.RED}[!] Group already exists{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            # Create new group
            groups[group_name] = {
                "createdAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "accounts": []
            }
            
            # Save updated groups
            with open("account_groups.json", "w") as f:
                json.dump(groups, f, indent=2)
            
            print(f"{Fore.GREEN}[+] Group '{group_name}' created successfully{Style.RESET_ALL}")
        elif choice == '3':
            # Add account to group
            if not groups:
                print(f"{Fore.YELLOW}[!] No groups found. Please create a group first.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}[+] Found {len(groups)} groups:{Style.RESET_ALL}")
            for i, group_name in enumerate(groups.keys()):
                print(f"{Fore.CYAN}[{Fore.GREEN}{i+1}{Fore.CYAN}] {Fore.WHITE}{group_name}{Style.RESET_ALL}")
            
            group_choice = input(f"{Fore.GREEN}Enter group number: {Style.RESET_ALL}")
            
            try:
                group_idx = int(group_choice) - 1
                if group_idx < 0 or group_idx >= len(groups):
                    print(f"{Fore.RED}[!] Invalid group number{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                group_name = list(groups.keys())[group_idx]
                
                print(f"{Fore.GREEN}[+] Found {len(accounts)} accounts:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
                print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Tasks{Fore.CYAN}  |  {Fore.YELLOW}Wallet{Fore.CYAN}  |  {Fore.YELLOW}Created{Fore.CYAN}  ║")
                print(f"╠════════════════════════════════════════════════════════════════════════════╣")
                
                for i, account in enumerate(accounts):
                    email = account.get("email", "N/A")
                    tasks = account.get("tasksCompleted", 0)
                    wallet = account.get("wallet", {}).get("address", "N/A")
                    if wallet != "N/A":
                        wallet = wallet[:6] + "..." + wallet[-4:]
                    created = account.get("createdAt", "N/A")
                    if created != "N/A":
                        try:
                            created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                            created = created_date.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    
                    print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{tasks}/7{Fore.CYAN}  |  {Fore.WHITE}{wallet}{Fore.CYAN}  |  {Fore.WHITE}{created}{Fore.CYAN}  ║")
                
                print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
                
                account_choice = input(f"{Fore.GREEN}Enter account number to add to group '{group_name}': {Style.RESET_ALL}")
                
                try:
                    account_idx = int(account_choice) - 1
                    if account_idx < 0 or account_idx >= len(accounts):
                        print(f"{Fore.RED}[!] Invalid account number{Style.RESET_ALL}")
                        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                        return
                    
                    account = accounts[account_idx]
                    email = account.get("email", "")
                    
                    # Check if account is already in group
                    if email in groups[group_name]["accounts"]:
                        print(f"{Fore.YELLOW}[!] Account already in group{Style.RESET_ALL}")
                        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                        return
                    
                    # Add account to group
                    groups[group_name]["accounts"].append(email)
                    
                    # Save updated groups
                    with open("account_groups.json", "w") as f:
                        json.dump(groups, f, indent=2)
                    
                    print(f"{Fore.GREEN}[+] Account added to group '{group_name}' successfully{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
        elif choice == '4':
            # Remove account from group
            if not groups:
                print(f"{Fore.YELLOW}[!] No groups found. Please create a group first.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}[+] Found {len(groups)} groups:{Style.RESET_ALL}")
            for i, group_name in enumerate(groups.keys()):
                print(f"{Fore.CYAN}[{Fore.GREEN}{i+1}{Fore.CYAN}] {Fore.WHITE}{group_name}{Style.RESET_ALL}")
            
            group_choice = input(f"{Fore.GREEN}Enter group number: {Style.RESET_ALL}")
            
            try:
                group_idx = int(group_choice) - 1
                if group_idx < 0 or group_idx >= len(groups):
                    print(f"{Fore.RED}[!] Invalid group number{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                group_name = list(groups.keys())[group_idx]
                group_accounts = groups[group_name]["accounts"]
                
                if not group_accounts:
                    print(f"{Fore.YELLOW}[!] No accounts in group '{group_name}'{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                print(f"{Fore.GREEN}[+] Found {len(group_accounts)} accounts in group '{group_name}':{Style.RESET_ALL}")
                for i, email in enumerate(group_accounts):
                    print(f"{Fore.CYAN}[{Fore.GREEN}{i+1}{Fore.CYAN}] {Fore.WHITE}{email}{Style.RESET_ALL}")
                
                account_choice = input(f"{Fore.GREEN}Enter account number to remove from group '{group_name}': {Style.RESET_ALL}")
                
                try:
                    account_idx = int(account_choice) - 1
                    if account_idx < 0 or account_idx >= len(group_accounts):
                        print(f"{Fore.RED}[!] Invalid account number{Style.RESET_ALL}")
                        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                        return
                    
                    email = group_accounts[account_idx]
                    
                    # Remove account from group
                    groups[group_name]["accounts"].remove(email)
                    
                    # Save updated groups
                    with open("account_groups.json", "w") as f:
                        json.dump(groups, f, indent=2)
                    
                    print(f"{Fore.GREEN}[+] Account removed from group '{group_name}' successfully{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
        elif choice == '5':
            # Delete group
            if not groups:
                print(f"{Fore.YELLOW}[!] No groups found. Please create a group first.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}[+] Found {len(groups)} groups:{Style.RESET_ALL}")
            for i, group_name in enumerate(groups.keys()):
                print(f"{Fore.CYAN}[{Fore.GREEN}{i+1}{Fore.CYAN}] {Fore.WHITE}{group_name}{Style.RESET_ALL}")
            
            group_choice = input(f"{Fore.GREEN}Enter group number to delete: {Style.RESET_ALL}")
            
            try:
                group_idx = int(group_choice) - 1
                if group_idx < 0 or group_idx >= len(groups):
                    print(f"{Fore.RED}[!] Invalid group number{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                group_name = list(groups.keys())[group_idx]
                
                confirm = input(f"{Fore.RED}Are you sure you want to delete group '{group_name}'? (y/n): {Style.RESET_ALL}")
                
                if confirm.lower() == 'y':
                    # Delete group
                    del groups[group_name]
                    
                    # Save updated groups
                    with open("account_groups.json", "w") as f:
                        json.dump(groups, f, indent=2)
                    
                    print(f"{Fore.GREEN}[+] Group '{group_name}' deleted successfully{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[*] Operation cancelled{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
        elif choice == '6':
            # View accounts in group
            if not groups:
                print(f"{Fore.YELLOW}[!] No groups found. Please create a group first.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}[+] Found {len(groups)} groups:{Style.RESET_ALL}")
            for i, group_name in enumerate(groups.keys()):
                print(f"{Fore.CYAN}[{Fore.GREEN}{i+1}{Fore.CYAN}] {Fore.WHITE}{group_name}{Style.RESET_ALL}")
            
            group_choice = input(f"{Fore.GREEN}Enter group number: {Style.RESET_ALL}")
            
            try:
                group_idx = int(group_choice) - 1
                if group_idx < 0 or group_idx >= len(groups):
                    print(f"{Fore.RED}[!] Invalid group number{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                group_name = list(groups.keys())[group_idx]
                group_accounts = groups[group_name]["accounts"]
                
                if not group_accounts:
                    print(f"{Fore.YELLOW}[!] No accounts in group '{group_name}'{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                # Find accounts in group
                group_account_data = []
                for email in group_accounts:
                    for account in accounts:
                        if account.get("email", "") == email:
                            group_account_data.append(account)
                            break
                
                print(f"{Fore.GREEN}[+] Found {len(group_account_data)} accounts in group '{group_name}':{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
                print(f"║  {Fore.YELLOW}ID{Fore.CYAN}  |  {Fore.YELLOW}Email{Fore.CYAN}  |  {Fore.YELLOW}Tasks{Fore.CYAN}  |  {Fore.YELLOW}Wallet{Fore.CYAN}  |  {Fore.YELLOW}Created{Fore.CYAN}  ║")
                print(f"╠════════════════════════════════════════════════════════════════════════════╣")
                
                for i, account in enumerate(group_account_data):
                    email = account.get("email", "N/A")
                    tasks = account.get("tasksCompleted", 0)
                    wallet = account.get("wallet", {}).get("address", "N/A")
                    if wallet != "N/A":
                        wallet = wallet[:6] + "..." + wallet[-4:]
                    created = account.get("createdAt", "N/A")
                    if created != "N/A":
                        try:
                            created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                            created = created_date.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    
                    print(f"║  {Fore.GREEN}{i+1:02d}{Fore.CYAN}  |  {Fore.WHITE}{email}{Fore.CYAN}  |  {Fore.WHITE}{tasks}/7{Fore.CYAN}  |  {Fore.WHITE}{wallet}{Fore.CYAN}  |  {Fore.WHITE}{created}{Fore.CYAN}  ║")
                
                print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
                
                # Ask if user wants to export accounts
                export = input(f"{Fore.YELLOW}Do you want to export these accounts to CSV? (y/n): {Style.RESET_ALL}")
                if export.lower() == 'y':
                    export_accounts_to_csv(group_account_data)
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error managing account groups: {str(e)}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

=======
>>>>>>> e7354fb9863b184dadd86cf14240a7ae60918c0e
def main_menu():
    """Display the main menu"""
    while True:
        clear_screen()
        print_banner()
        
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗")
        print(f"║                                {Fore.YELLOW}MAIN MENU{Fore.CYAN}                                  ║")
        print(f"╠════════════════════════════════════════════════════════════════════════════╣")
        print(f"║  {Fore.GREEN}[1]{Fore.CYAN} Add Proxy                                                                                ║")
        print(f"║  {Fore.GREEN}[2]{Fore.CYAN} Delete All Proxies                                                                      ║")
        print(f"║  {Fore.GREEN}[3]{Fore.CYAN} Add Referral Code                                                                       ║")
        print(f"║  {Fore.GREEN}[4]{Fore.CYAN} Delete Referral Code                                                                    ║")
        print(f"║  {Fore.GREEN}[5]{Fore.CYAN} Start Account Creation                                                                  ║")
        print(f"║  {Fore.GREEN}[6]{Fore.CYAN} View Accounts                                                                           ║")
        print(f"║  {Fore.GREEN}[7]{Fore.CYAN} Test Proxies                                                                            ║")
        print(f"║  {Fore.GREEN}[8]{Fore.CYAN} View Statistics                                                                         ║")
        print(f"║  {Fore.GREEN}[9]{Fore.CYAN} Delete All Accounts                                                                     ║")
        print(f"║  {Fore.GREEN}[10]{Fore.CYAN} Backup Accounts                                                                        ║")
        print(f"║  {Fore.GREEN}[11]{Fore.CYAN} Restore Accounts                                                                       ║")
<<<<<<< HEAD
        print(f"║  {Fore.GREEN}[12]{Fore.CYAN} Import Proxies                                                                         ║")
        print(f"║  {Fore.GREEN}[13]{Fore.CYAN} Export Proxies                                                                         ║")
        print(f"║  {Fore.GREEN}[14]{Fore.CYAN} Rotate Proxies                                                                         ║")
        print(f"║  {Fore.GREEN}[15]{Fore.CYAN} Search Accounts                                                                        ║")
        print(f"║  {Fore.GREEN}[16]{Fore.CYAN} Filter Accounts                                                                        ║")
        print(f"║  {Fore.GREEN}[17]{Fore.CYAN} Complete Tasks                                                                         ║")
        print(f"║  {Fore.GREEN}[18]{Fore.CYAN} Manage Wallets                                                                         ║")
        print(f"║  {Fore.GREEN}[19]{Fore.CYAN} Manage Account Groups                                                                  ║")
=======
>>>>>>> e7354fb9863b184dadd86cf14240a7ae60918c0e
        print(f"║  {Fore.GREEN}[0]{Fore.CYAN} Exit                                                                                    ║")
        print(f"╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '1':
            add_proxy()
        elif choice == '2':
            delete_proxies()
        elif choice == '3':
            add_referral_code()
        elif choice == '4':
            delete_referral_code()
        elif choice == '5':
            start_account_creation()
        elif choice == '6':
            view_accounts()
        elif choice == '7':
            test_proxies()
        elif choice == '8':
            view_statistics()
        elif choice == '9':
            delete_accounts()
        elif choice == '10':
            backup_accounts()
        elif choice == '11':
            restore_accounts()
<<<<<<< HEAD
        elif choice == '12':
            import_proxies()
        elif choice == '13':
            export_proxies()
        elif choice == '14':
            rotate_proxies()
        elif choice == '15':
            search_accounts()
        elif choice == '16':
            filter_accounts()
        elif choice == '17':
            complete_tasks()
        elif choice == '18':
            manage_wallets()
        elif choice == '19':
            manage_account_groups()
=======
>>>>>>> e7354fb9863b184dadd86cf14240a7ae60918c0e
        elif choice == '0':
            clear_screen()
            print(f"{Fore.GREEN}[+] Thank you for using Bilipad Manager{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}[!] Invalid choice. Please try again.{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_screen()
        print(f"{Fore.GREEN}[+] Thank you for using Bilipad Manager{Style.RESET_ALL}")
<<<<<<< HEAD
        sys.exit(0) 
=======
        sys.exit(0) 
>>>>>>> e7354fb9863b184dadd86cf14240a7ae60918c0e
