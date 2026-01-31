import os
import time
from datetime import datetime
import csv

CONFIG_FILE = "filter_rules.txt"
OUTPUT_FILE = "scan_results.csv"

TARGET_LOGS = [
    "/var/log/test.log",
    "/var/log/auth.log",
    "/var/log/syslog", 
    "/var/log/nginx/access.log", 
    "/var/log/ufw.log"
]

def clear_console():
    command = 'cls' if os.name == 'nt' else 'clear'  
    os.system(command)

def load_rules():
    rules = []
    
    if not os.path.exists(CONFIG_FILE):
        defaults = "error,System Error\nFailed password,Auth Failure\nUFW BLOCK,Firewall Block\nroot,Root Activity"
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:  
            f.write(defaults)
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "," in line:
                    parts = line.strip().split(",")  
                    rules.append({"keyword": parts[0], "tag": parts[1]})
    except Exception as e:
        print(f"Error: {e}")
        
    return rules

def check_line(line, rules):
    for rule in rules:
        if rule["keyword"].lower() in line.lower():  
            return {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Type": rule["tag"],
                "Payload": line.strip()[:100]
            }
    return None

def scan_file(filepath):
    print(f"\nScanning target: {filepath}...")
    
    if not os.path.exists(filepath):
        print("Error: File not found inside Docker container!")
        return []

    rules = load_rules()
    findings = []
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:  
            lines = f.readlines()
            for line in lines:
                result = check_line(line, rules)
                if result:
                    result["File"] = filepath
                    findings.append(result)
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    return findings

def save_to_csv(data):
    if not data:
        print("No data to export.")
        return

    file_exists = os.path.exists(OUTPUT_FILE)
    
    try:
        with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Timestamp", "File", "Type", "Payload"]) 
            
            if not file_exists:
                writer.writeheader()
                
            writer.writerows(data)
        print(f"Success! Saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

def live_monitor(filepath):
    rules = load_rules()
    print(f"\n--- LOG GUARD ACTIVE MONITOR: {filepath} ---")
    print("Stop: CTRL + C\n")

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2) 
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                
                hit = check_line(line, rules)
                if hit:
                    print(f"ALERT! [{hit['Timestamp']}] {hit['Type']} detected.")
                    
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except FileNotFoundError:
        print("File not found.")

def main_menu():
    current_target = TARGET_LOGS[0]
    last_scan_data = []
    
    while True:
        clear_console()
        print("********************************")
        print("*      LOG GUARD TOOL v1.0     *")
        print("********************************")
        print(f"Target: {current_target}")
        print(f"Memory: {len(last_scan_data)} items ready to export")
        print("--------------------------------")
        print("1. Change Target Log")
        print("2. Scan Log (Display Only)")
        print("3. Export Last Scan to CSV")
        print("4. Start Live Monitor")
        print("5. Exit")
        
        choice = input("\nSelect > ")
        
        if choice == "1":
            print("\nAvailable Logs:")
            for i, l in enumerate(TARGET_LOGS):
                print(f"{i+1} - {l}")
            try:
                sel = int(input("Number: "))
                if 1 <= sel <= len(TARGET_LOGS):
                    current_target = TARGET_LOGS[sel-1]
            except:
                pass

        elif choice == "2":
            last_scan_data = scan_file(current_target)
            print(f"\nScan complete. Found {len(last_scan_data)} suspicious events.")
            
            if len(last_scan_data) > 0:
                print("\nLast 5 events:")
                for item in last_scan_data[-5:]:
                    print(f"- [{item['Timestamp']}] {item['Type']}: {item['Payload'][:50]}...")
                print("\n(Tip: Use Option 3 to save all results to CSV)")
            
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            if len(last_scan_data) > 0:
                save_to_csv(last_scan_data)
            else:
                print("\nNo data to export! Please run 'Scan Log' first.")
            
            input("\nPress Enter...")

        elif choice == "4":
            live_monitor(current_target)

        elif choice == "5":
            break

if __name__ == "__main__":
    main_menu()