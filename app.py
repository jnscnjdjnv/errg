from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import time
import threading
import uuid
import random
import requests
from eth_account import Account
from web3 import Web3
import logging
from datetime import datetime
import csv
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bilipad_web.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Delete the existing database file
if os.path.exists('bilipad.db'):
    os.remove('bilipad.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bilipad.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    referral_code = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128))
    user_id = db.Column(db.String(128))
    device_id = db.Column(db.String(128))
    auth_token = db.Column(db.Text)
    wallet_address = db.Column(db.String(128))
    wallet_private_key = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    proxy = db.Column(db.String(256))
    tasks_completed = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all database tables
with app.app_context():
    db.create_all()

# Constants
BASE_URL = 'https://billipad.finance/api'
REFERRAL_CODE_FILE = 'referral_code.txt'
ACCOUNTS_FILE = 'accounts.json'
EMAIL_DOMAIN = 'ptct.net'
PROXIES_FILE = 'proxies.txt'
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
TASK_RETRY_COUNT = 3
TASK_RETRY_DELAY = 5

# Global variables
accounts = []
proxies = []
referral_code = ''
account_creation_status = {
    'running': False,
    'created': 0,
    'failed': 0,
    'total': 0,
    'current_account': '',
    'message': '',
    'last_updated': ''
}

# Helper functions
def update_account_status(key, value):
    """Update account creation status and set last_updated timestamp"""
    account_creation_status[key] = value
    account_creation_status['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")

def load_referral_code():
    """Load referral code from file"""
    global referral_code
    try:
        if not os.path.exists(REFERRAL_CODE_FILE):
            logging.warning(f"[!] {REFERRAL_CODE_FILE} not found, using empty referral code")
            referral_code = ''
            return
        
        with open(REFERRAL_CODE_FILE, 'r') as f:
            referral_code = f.read().strip()
        
        if not referral_code:
            logging.warning("[!] Referral code is empty")
        else:
            logging.info(f"[+] Loaded referral code: {referral_code}")
    except Exception as e:
        logging.error(f"[-] Error loading referral code: {str(e)}")
        referral_code = ''

def load_proxies():
    """Load proxies from file"""
    global proxies
    try:
        if not os.path.exists(PROXIES_FILE):
            logging.error(f"[-] {PROXIES_FILE} not found")
            return None
        
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxy_lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if not proxy_lines:
            logging.warning(f"[!] No proxies found in {PROXIES_FILE}")
            return None
        
        valid_proxies = []
        for line in proxy_lines:
            try:
                proxy = line.strip()
                
                # Handle different proxy formats
                if '@' in proxy:
                    # Format: username:password@host:port
                    auth, host_port = proxy.split('@')
                    if ':' in auth:
                        username, password = auth.split(':')
                    else:
                        username, password = auth, ''
                    
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, ''
                    
                    proxy_url = f"http://{username}:{password}@{host}:{port}"
                else:
                    # Format: host:port
                    if ':' in proxy:
                        host, port = proxy.split(':')
                    else:
                        host, port = proxy, ''
                    
                    proxy_url = f"http://{host}:{port}"
                
                if not host or not port:
                    logging.warning(f"[!] Invalid proxy format: {line}")
                    continue
                
                valid_proxies.append(proxy_url)
            except Exception as e:
                logging.warning(f"[!] Error parsing proxy line '{line}': {str(e)}")
        
        logging.info(f"[+] Successfully loaded {len(valid_proxies)} proxies")
        return valid_proxies
    except Exception as e:
        logging.error(f"[-] Error loading proxies: {str(e)}")
        return None

def get_random_proxy():
    """Get a random proxy from the list"""
    if not proxies:
        logging.warning("[!] No valid proxies available, proceeding without proxy")
        return None
    
    proxy = random.choice(proxies)
    logging.info(f"[*] Using proxy: {proxy}")
    return proxy

def create_random_email():
    """Create a random email and credentials"""
    username = f"user{random.randint(1000000, 9999999)}"
    email = f"{username}@{EMAIL_DOMAIN}"
    password = f"Pass{random.randint(100000, 999999)}"
    
    logging.info(f"[+] Created email: {email}")
    
    return {
        "username": username,
        "email": email,
        "password": password,
        "deviceId": str(uuid.uuid4())
    }

def generate_wallet():
    """Generate a new Ethereum wallet"""
    account = Account.create()
    return {
        "address": account.address,
        "privateKey": account.key.hex()
    }

def create_headers(auth_token=None, referer='signup'):
    """Create headers for API requests"""
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Brave\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "Referer": f"https://billipad.finance/{referer}",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    
    if auth_token:
        headers["cookie"] = f"authToken={auth_token}"
    
    return headers

def make_request(method, url, data=None, headers=None, proxy=None, timeout=REQUEST_TIMEOUT, retry_count=3):
    """Make HTTP request with proxy support and retry logic"""
    for attempt in range(retry_count):
        try:
            proxies = None
            if proxy:
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            else:
                response = requests.post(url, json=data, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            
            # Check for 402 Payment Required error
            if response.status_code == 402:
                logging.error(f"[-] Payment Required error: {response.text}")
                try:
                    error_data = response.json()
                    logging.error(f"[-] Error details: {error_data}")
                except:
                    pass
                raise Exception(f"Payment Required: {response.text}")
            
            response.raise_for_status()
            return response.json(), response.headers
        except requests.exceptions.RequestException as e:
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                logging.warning(f"Request failed (attempt {attempt+1}/{retry_count}): {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Request error after {retry_count} attempts: {str(e)}")
                raise

def register_user(credentials, proxy):
    """Register a new user"""
    try:
        username = credentials["username"]
        email = credentials["email"]
        password = credentials["password"]
        device_id = credentials["deviceId"]
        
        headers = create_headers(None, f'signup?ref={referral_code}')
        
        # Add additional headers that might help
        headers.update({
            "Origin": "https://billipad.finance",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })
        
        data = {
            "username": username,
            "email": email,
            "password": password,
            "deviceId": device_id,
            "referralLink": f'https://Billipad.finance/ref/{referral_code}'
        }
        
        # Try to get the signup page first to get any necessary cookies
        try:
            signup_url = f"https://billipad.finance/signup?ref={referral_code}"
            requests.get(signup_url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, verify=False, timeout=REQUEST_TIMEOUT)
            logging.info("[+] Visited signup page to get cookies")
        except Exception as e:
            logging.warning(f"[!] Failed to visit signup page: {str(e)}")
        
        # Wait a bit before making the actual request
        time.sleep(2)
        
        response, _ = make_request('POST', f"{BASE_URL}/signup", data, headers, proxy)
        
        logging.info(f"[+] Successfully registered: {email}")
        return response
    except Exception as e:
        logging.error(f"[-] Registration failed for {credentials['email']}: {str(e)}")
        raise

def login_user(credentials, proxy):
    """Login a user"""
    try:
        email = credentials["email"]
        password = credentials["password"]
        device_id = credentials["deviceId"]
        
        headers = create_headers(None, 'login')
        
        # Add additional headers that might help
        headers.update({
            "Origin": "https://billipad.finance",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })
        
        data = {
            "email": email,
            "password": password,
            "deviceId": device_id
        }
        
        # Try to get the login page first to get any necessary cookies
        try:
            login_url = "https://billipad.finance/login"
            requests.get(login_url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, verify=False, timeout=REQUEST_TIMEOUT)
            logging.info("[+] Visited login page to get cookies")
        except Exception as e:
            logging.warning(f"[!] Failed to visit login page: {str(e)}")
        
        # Wait a bit before making the actual request
        time.sleep(2)
        
        response, response_headers = make_request('POST', f"{BASE_URL}/login", data, headers, proxy)
        
        if not response.get('user') or not response['user'].get('id'):
            raise Exception('No valid user data received')
        
        auth_token = response.get('token')
        
        if not auth_token:
            set_cookie = response_headers.get('set-cookie')
            if set_cookie:
                cookie_string = set_cookie if isinstance(set_cookie, str) else '; '.join(set_cookie)
                token_match = re.search(r'authToken=([^;]+)', cookie_string)
                if token_match and token_match.group(1):
                    auth_token = token_match.group(1)
                    logging.info('[+] Token from cookie')
        
        if not auth_token:
            logging.warning('[!] No token found')
        
        logging.info(f"[+] Logged in: {email}")
        if auth_token:
            logging.info(f"[+] Token: {auth_token[:20]}...")
        
        return {
            "token": auth_token,
            "user": response['user']
        }
    except Exception as e:
        logging.error(f"[-] Login failed for {credentials['email']}: {str(e)}")
        raise

def check_auth(auth_token, proxy):
    """Check authentication status"""
    try:
        headers = create_headers(auth_token, 'dashboard')
        
        response, _ = make_request('GET', f"{BASE_URL}/auth-check", headers=headers, proxy=proxy)
        
        logging.info('[+] Auth check OK')
        return response
    except Exception as e:
        logging.error(f"[-] Auth check failed: {str(e)}")
        raise

def complete_task(user_id, auth_token, task_index, proxy):
    """Complete a task for a user with retry logic"""
    for attempt in range(TASK_RETRY_COUNT):
        try:
            headers = create_headers(auth_token, 'dashboard')
            
            data = {
                "action": "updateTask",
                "value": 10,
                "taskIndex": task_index,
                "clicks": 2
            }
            
            response, _ = make_request('POST', f"{BASE_URL}/referral?userId={user_id}", data, headers, proxy)
            
            logging.info(f"[+] Task {task_index + 1} done for user: {user_id}")
            return response
        except Exception as e:
            if attempt < TASK_RETRY_COUNT - 1:
                wait_time = TASK_RETRY_DELAY * (attempt + 1)
                logging.warning(f"[-] Task {task_index + 1} failed (attempt {attempt+1}/{TASK_RETRY_COUNT}): {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"[-] Task {task_index + 1} failed after {TASK_RETRY_COUNT} attempts: {str(e)}")
                raise

def submit_withdrawal_address(user_id, wallet_address, auth_token, proxy):
    """Submit withdrawal address for a user"""
    try:
        headers = create_headers(auth_token, 'dashboard')
        
        data = {
            "userId": user_id,
            "walletAddress": wallet_address
        }
        
        response, _ = make_request('POST', f"{BASE_URL}/withdraw", data, headers, proxy)
        
        logging.info(f"[+] Withdrawal address set for user: {user_id}")
        return response
    except Exception as e:
        logging.error(f"[-] Withdrawal address failed: {str(e)}")
        raise

def save_accounts():
    """Save accounts to file"""
    try:
        # Create the file if it doesn't exist
        if not os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump([], f)
            logging.info(f"[+] Created new {ACCOUNTS_FILE} file")
        
        # Save the accounts
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        logging.info(f"[+] Saved {len(accounts)} accounts to {ACCOUNTS_FILE}")
    except Exception as e:
        logging.error(f"[-] Failed to save accounts: {str(e)}")

def create_account():
    """Create a new account"""
    global account_creation_status
    
    try:
        # Generate random email and password
        email = f"user{random.randint(100000, 999999)}@{EMAIL_DOMAIN}"
        password = f"Pass{random.randint(100000, 999999)}"
        
        # Update status
        update_account_status('current_account', email)
        update_account_status('message', f"Creating account: {email}")
        
        # Create account
        credentials = {
            'email': email,
            'password': password,
            'deviceId': str(uuid.uuid4())
        }
        
        # Register user
        register_user(credentials)
        
        # Login user
        auth_token = login_user(credentials)
        
        # Complete tasks
        for task_index in range(7):
            update_account_status('message', f"Completing task {task_index + 1}/7 for {email}")
            complete_task(auth_token, task_index)
            time.sleep(1)
        
        # Set withdrawal address
        update_account_status('message', f"Setting withdrawal address for {email}")
        wallet = generate_wallet()
        submit_withdrawal_address(auth_token, wallet['address'])
        
        # Save account
        account_data = {
            'email': email,
            'password': password,
            'auth_token': auth_token,
            'wallet': wallet,
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        accounts.append(account_data)
        save_accounts()
        
        update_account_status('created', account_creation_status['created'] + 1)
        update_account_status('message', f"Account created: {email}")
        return account_data
    except Exception as e:
        update_account_status('failed', account_creation_status['failed'] + 1)
        update_account_status('message', f"Failed to create account: {str(e)}")
        return None

def process_accounts(count):
    """Process multiple accounts"""
    global account_creation_status
    
    for i in range(count):
        if not account_creation_status['running']:
            update_account_status('message', "Account creation stopped by user")
            break
        
        update_account_status('message', f"Processing account {i + 1}/{count}")
        
        try:
            account_data = create_account()
            if account_data:
                update_account_status('created', account_creation_status['created'] + 1)
                update_account_status('message', f"Account created: {account_data['email']}")
            else:
                update_account_status('failed', account_creation_status['failed'] + 1)
                update_account_status('message', f"Failed to create account")
        except Exception as e:
            update_account_status('failed', account_creation_status['failed'] + 1)
            update_account_status('message', f"Error: {str(e)}")
        
        if i < count - 1 and account_creation_status['running']:
            time.sleep(5)  # Wait between accounts
    
    update_account_status('running', False)
    update_account_status('message', f"Done: {account_creation_status['created']} OK, {account_creation_status['failed']} failed")
    logging.info(f"\n[+] Done: {account_creation_status['created']} OK, {account_creation_status['failed']} failed")
    logging.info(f"[*] Saved to {ACCOUNTS_FILE}")

def start_account_creation(count):
    """Start account creation process"""
    global account_creation_status
    
    # Reset status
    update_account_status('running', True)
    update_account_status('total', count)
    update_account_status('created', 0)
    update_account_status('failed', 0)
    update_account_status('message', "Starting account creation process")
    
    # Start account creation in a separate thread
    thread = threading.Thread(target=process_accounts, args=(count,))
    thread.daemon = True
    thread.start()
    
    return True

def stop_account_creation():
    """Stop account creation process"""
    global account_creation_status
    
    update_account_status('running', False)
    update_account_status('message', "Stopping account creation process...")
    
    return True

def export_accounts_to_csv():
    """Export accounts to CSV file"""
    try:
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
                    'createdAt': account.get('created_at', ''),
                    'proxy': account.get('proxy', ''),
                    'tasksCompleted': account.get('tasks_completed', 0)
                }
                writer.writerow(row)
        
        logging.info(f"[+] Accounts exported to {filename}")
        return filename
    except Exception as e:
        logging.error(f"[-] Error exporting accounts: {str(e)}")
        return None

def backup_accounts():
    """Create a backup of accounts.json"""
    try:
        if not os.path.exists(ACCOUNTS_FILE):
            logging.error(f"[-] No accounts found. Please create accounts first.")
            return None
        
        # Create backup directory if it doesn't exist
        if not os.path.exists("backups"):
            os.makedirs("backups")
        
        # Create backup file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/accounts_backup_{timestamp}.json"
        
        # Copy accounts.json to backup file
        shutil.copy2(ACCOUNTS_FILE, backup_file)
        
        logging.info(f"[+] Accounts backed up to {backup_file}")
        return backup_file
    except Exception as e:
        logging.error(f"[-] Error backing up accounts: {str(e)}")
        return None

def restore_accounts(backup_file):
    """Restore accounts from a backup"""
    try:
        if not os.path.exists(backup_file):
            logging.error(f"[-] Backup file not found: {backup_file}")
            return False
        
        # Copy backup file to accounts.json
        shutil.copy2(backup_file, ACCOUNTS_FILE)
        
        # Reload accounts
        global accounts
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
        
        logging.info(f"[+] Accounts restored from {backup_file}")
        return True
    except Exception as e:
        logging.error(f"[-] Error restoring accounts: {str(e)}")
        return False

def get_backup_files():
    """Get list of backup files"""
    try:
        if not os.path.exists("backups"):
            return []
        
        backup_files = [f for f in os.listdir("backups") if f.startswith("accounts_backup_") and f.endswith(".json")]
        
        # Sort backup files by date (newest first)
        backup_files.sort(reverse=True)
        
        return backup_files
    except Exception as e:
        logging.error(f"[-] Error getting backup files: {str(e)}")
        return []

# Initialize data
def init_data():
    """Initialize data from files"""
    global accounts, proxies, referral_code
    
    # Load referral code
    load_referral_code()
    
    # Load proxies
    proxies = load_proxies()
    
    # Load existing accounts if file exists
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                accounts = json.load(f)
            logging.info(f"[+] Loaded {len(accounts)} existing accounts from {ACCOUNTS_FILE}")
        except Exception as e:
            logging.error(f"[-] Error loading existing accounts: {str(e)}")
            accounts = []
    else:
        # Create empty accounts file if it doesn't exist
        try:
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump([], f)
            logging.info(f"[+] Created new {ACCOUNTS_FILE} file")
        except Exception as e:
            logging.error(f"[-] Error creating accounts file: {str(e)}")

# Initialize data on startup
init_data()

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        account_count = Account.query.filter_by(owner_id=current_user.id).count()
        return render_template('index.html', 
                            referral_code=current_user.referral_code,
                            account_count=account_count,
                            proxy_count=len(proxies),
                            account_creation_status=get_account_creation_status())
    else:
        return render_template('index.html', 
                            referral_code=None,
                            account_count=0,
                            proxy_count=len(proxies),
                            account_creation_status={'running': False, 'created': 0, 'failed': 0, 'total': 0, 'last_updated': ''})

@app.route('/accounts')
@login_required
def view_accounts():
    """View all accounts"""
    accounts = Account.query.filter_by(owner_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)

@app.route('/proxies')
def view_proxies():
    """View all proxies"""
    global proxies
    try:
        # Refresh proxies list before displaying
        proxies = load_proxies()
        if proxies is None:
            proxies = []
        return render_template('proxies.html', proxies=proxies)
    except Exception as e:
        logging.error(f"Error loading proxies: {str(e)}")
        flash('Error loading proxies. Please check the logs for details.', 'error')
        return render_template('proxies.html', proxies=[])

@app.route('/add_proxy', methods=['GET', 'POST'])
def add_proxy():
    """Add a proxy"""
    if request.method == 'POST':
        proxy = request.form.get('proxy', '').strip()
        
        if not proxy:
            flash('Proxy cannot be empty', 'error')
            return redirect(url_for('add_proxy'))
        
        try:
            with open(PROXIES_FILE, "a") as f:
                f.write(proxy + "\n")
            
            # Reload proxies
            global proxies
            proxies = load_proxies()
            
            flash('Proxy added successfully', 'success')
            return redirect(url_for('view_proxies'))
        except Exception as e:
            flash(f'Error adding proxy: {str(e)}', 'error')
            return redirect(url_for('add_proxy'))
    
    return render_template('add_proxy.html')

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import time
import threading
import uuid
import random
import requests
from eth_account import Account
from web3 import Web3
import logging
from datetime import datetime
import csv
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bilipad_web.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Delete the existing database file
if os.path.exists('bilipad.db'):
    os.remove('bilipad.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bilipad.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    referral_code = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128))
    user_id = db.Column(db.String(128))
    device_id = db.Column(db.String(128))
    auth_token = db.Column(db.Text)
    wallet_address = db.Column(db.String(128))
    wallet_private_key = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    proxy = db.Column(db.String(256))
    tasks_completed = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all database tables
with app.app_context():
    db.create_all()

# Constants
BASE_URL = 'https://billipad.finance/api'
REFERRAL_CODE_FILE = 'referral_code.txt'
ACCOUNTS_FILE = 'accounts.json'
EMAIL_DOMAIN = 'ptct.net'
PROXIES_FILE = 'proxies.txt'
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
TASK_RETRY_COUNT = 3
TASK_RETRY_DELAY = 5

# Global variables
accounts = []
proxies = []
referral_code = ''
account_creation_status = {
    'running': False,
    'created': 0,
    'failed': 0,
    'total': 0,
    'current_account': '',
    'message': '',
    'last_updated': ''
}

# Helper functions
def update_account_status(key, value):
    """Update account creation status and set last_updated timestamp"""
    account_creation_status[key] = value
    account_creation_status['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")

def load_referral_code():
    """Load referral code from file"""
    global referral_code
    try:
        if not os.path.exists(REFERRAL_CODE_FILE):
            logging.warning(f"[!] {REFERRAL_CODE_FILE} not found, using empty referral code")
            referral_code = ''
            return
        
        with open(REFERRAL_CODE_FILE, 'r') as f:
            referral_code = f.read().strip()
        
        if not referral_code:
            logging.warning("[!] Referral code is empty")
        else:
            logging.info(f"[+] Loaded referral code: {referral_code}")
    except Exception as e:
        logging.error(f"[-] Error loading referral code: {str(e)}")
        referral_code = ''

def load_proxies():
    """Load proxies from file"""
    global proxies
    try:
        if not os.path.exists(PROXIES_FILE):
            logging.error(f"[-] {PROXIES_FILE} not found")
            return None
        
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxy_lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if not proxy_lines:
            logging.warning(f"[!] No proxies found in {PROXIES_FILE}")
            return None
        
        valid_proxies = []
        for line in proxy_lines:
            try:
                proxy = line.strip()
                
                # Handle different proxy formats
                if '@' in proxy:
                    # Format: username:password@host:port
                    auth, host_port = proxy.split('@')
                    if ':' in auth:
                        username, password = auth.split(':')
                    else:
                        username, password = auth, ''
                    
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, ''
                    
                    proxy_url = f"http://{username}:{password}@{host}:{port}"
                else:
                    # Format: host:port
                    if ':' in proxy:
                        host, port = proxy.split(':')
                    else:
                        host, port = proxy, ''
                    
                    proxy_url = f"http://{host}:{port}"
                
                if not host or not port:
                    logging.warning(f"[!] Invalid proxy format: {line}")
                    continue
                
                valid_proxies.append(proxy_url)
            except Exception as e:
                logging.warning(f"[!] Error parsing proxy line '{line}': {str(e)}")
        
        logging.info(f"[+] Successfully loaded {len(valid_proxies)} proxies")
        return valid_proxies
    except Exception as e:
        logging.error(f"[-] Error loading proxies: {str(e)}")
        return None

def get_random_proxy():
    """Get a random proxy from the list"""
    if not proxies:
        logging.warning("[!] No valid proxies available, proceeding without proxy")
        return None
    
    proxy = random.choice(proxies)
    logging.info(f"[*] Using proxy: {proxy}")
    return proxy

def create_random_email():
    """Create a random email and credentials"""
    username = f"user{random.randint(1000000, 9999999)}"
    email = f"{username}@{EMAIL_DOMAIN}"
    password = f"Pass{random.randint(100000, 999999)}"
    
    logging.info(f"[+] Created email: {email}")
    
    return {
        "username": username,
        "email": email,
        "password": password,
        "deviceId": str(uuid.uuid4())
    }

def generate_wallet():
    """Generate a new Ethereum wallet"""
    account = Account.create()
    return {
        "address": account.address,
        "privateKey": account.key.hex()
    }

def create_headers(auth_token=None, referer='signup'):
    """Create headers for API requests"""
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Brave\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "Referer": f"https://billipad.finance/{referer}",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    
    if auth_token:
        headers["cookie"] = f"authToken={auth_token}"
    
    return headers

def make_request(method, url, data=None, headers=None, proxy=None, timeout=REQUEST_TIMEOUT, retry_count=3):
    """Make HTTP request with proxy support and retry logic"""
    for attempt in range(retry_count):
        try:
            proxies = None
            if proxy:
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            else:
                response = requests.post(url, json=data, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            
            # Check for 402 Payment Required error
            if response.status_code == 402:
                logging.error(f"[-] Payment Required error: {response.text}")
                try:
                    error_data = response.json()
                    logging.error(f"[-] Error details: {error_data}")
                except:
                    pass
                raise Exception(f"Payment Required: {response.text}")
            
            response.raise_for_status()
            return response.json(), response.headers
        except requests.exceptions.RequestException as e:
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                logging.warning(f"Request failed (attempt {attempt+1}/{retry_count}): {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Request error after {retry_count} attempts: {str(e)}")
                raise

def register_user(credentials, proxy):
    """Register a new user"""
    try:
        username = credentials["username"]
        email = credentials["email"]
        password = credentials["password"]
        device_id = credentials["deviceId"]
        
        headers = create_headers(None, f'signup?ref={referral_code}')
        
        # Add additional headers that might help
        headers.update({
            "Origin": "https://billipad.finance",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })
        
        data = {
            "username": username,
            "email": email,
            "password": password,
            "deviceId": device_id,
            "referralLink": f'https://Billipad.finance/ref/{referral_code}'
        }
        
        # Try to get the signup page first to get any necessary cookies
        try:
            signup_url = f"https://billipad.finance/signup?ref={referral_code}"
            requests.get(signup_url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, verify=False, timeout=REQUEST_TIMEOUT)
            logging.info("[+] Visited signup page to get cookies")
        except Exception as e:
            logging.warning(f"[!] Failed to visit signup page: {str(e)}")
        
        # Wait a bit before making the actual request
        time.sleep(2)
        
        response, _ = make_request('POST', f"{BASE_URL}/signup", data, headers, proxy)
        
        logging.info(f"[+] Successfully registered: {email}")
        return response
    except Exception as e:
        logging.error(f"[-] Registration failed for {credentials['email']}: {str(e)}")
        raise

def login_user(credentials, proxy):
    """Login a user"""
    try:
        email = credentials["email"]
        password = credentials["password"]
        device_id = credentials["deviceId"]
        
        headers = create_headers(None, 'login')
        
        # Add additional headers that might help
        headers.update({
            "Origin": "https://billipad.finance",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })
        
        data = {
            "email": email,
            "password": password,
            "deviceId": device_id
        }
        
        # Try to get the login page first to get any necessary cookies
        try:
            login_url = "https://billipad.finance/login"
            requests.get(login_url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, verify=False, timeout=REQUEST_TIMEOUT)
            logging.info("[+] Visited login page to get cookies")
        except Exception as e:
            logging.warning(f"[!] Failed to visit login page: {str(e)}")
        
        # Wait a bit before making the actual request
        time.sleep(2)
        
        response, response_headers = make_request('POST', f"{BASE_URL}/login", data, headers, proxy)
        
        if not response.get('user') or not response['user'].get('id'):
            raise Exception('No valid user data received')
        
        auth_token = response.get('token')
        
        if not auth_token:
            set_cookie = response_headers.get('set-cookie')
            if set_cookie:
                cookie_string = set_cookie if isinstance(set_cookie, str) else '; '.join(set_cookie)
                token_match = re.search(r'authToken=([^;]+)', cookie_string)
                if token_match and token_match.group(1):
                    auth_token = token_match.group(1)
                    logging.info('[+] Token from cookie')
        
        if not auth_token:
            logging.warning('[!] No token found')
        
        logging.info(f"[+] Logged in: {email}")
        if auth_token:
            logging.info(f"[+] Token: {auth_token[:20]}...")
        
        return {
            "token": auth_token,
            "user": response['user']
        }
    except Exception as e:
        logging.error(f"[-] Login failed for {credentials['email']}: {str(e)}")
        raise

def check_auth(auth_token, proxy):
    """Check authentication status"""
    try:
        headers = create_headers(auth_token, 'dashboard')
        
        response, _ = make_request('GET', f"{BASE_URL}/auth-check", headers=headers, proxy=proxy)
        
        logging.info('[+] Auth check OK')
        return response
    except Exception as e:
        logging.error(f"[-] Auth check failed: {str(e)}")
        raise

def complete_task(user_id, auth_token, task_index, proxy):
    """Complete a task for a user with retry logic"""
    for attempt in range(TASK_RETRY_COUNT):
        try:
            headers = create_headers(auth_token, 'dashboard')
            
            data = {
                "action": "updateTask",
                "value": 10,
                "taskIndex": task_index,
                "clicks": 2
            }
            
            response, _ = make_request('POST', f"{BASE_URL}/referral?userId={user_id}", data, headers, proxy)
            
            logging.info(f"[+] Task {task_index + 1} done for user: {user_id}")
            return response
        except Exception as e:
            if attempt < TASK_RETRY_COUNT - 1:
                wait_time = TASK_RETRY_DELAY * (attempt + 1)
                logging.warning(f"[-] Task {task_index + 1} failed (attempt {attempt+1}/{TASK_RETRY_COUNT}): {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"[-] Task {task_index + 1} failed after {TASK_RETRY_COUNT} attempts: {str(e)}")
                raise

def submit_withdrawal_address(user_id, wallet_address, auth_token, proxy):
    """Submit withdrawal address for a user"""
    try:
        headers = create_headers(auth_token, 'dashboard')
        
        data = {
            "userId": user_id,
            "walletAddress": wallet_address
        }
        
        response, _ = make_request('POST', f"{BASE_URL}/withdraw", data, headers, proxy)
        
        logging.info(f"[+] Withdrawal address set for user: {user_id}")
        return response
    except Exception as e:
        logging.error(f"[-] Withdrawal address failed: {str(e)}")
        raise

def save_accounts():
    """Save accounts to file"""
    try:
        # Create the file if it doesn't exist
        if not os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump([], f)
            logging.info(f"[+] Created new {ACCOUNTS_FILE} file")
        
        # Save the accounts
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        logging.info(f"[+] Saved {len(accounts)} accounts to {ACCOUNTS_FILE}")
    except Exception as e:
        logging.error(f"[-] Failed to save accounts: {str(e)}")

def create_account():
    """Create a new account"""
    global account_creation_status
    
    try:
        # Generate random email and password
        email = f"user{random.randint(100000, 999999)}@{EMAIL_DOMAIN}"
        password = f"Pass{random.randint(100000, 999999)}"
        
        # Update status
        update_account_status('current_account', email)
        update_account_status('message', f"Creating account: {email}")
        
        # Create account
        credentials = {
            'email': email,
            'password': password,
            'deviceId': str(uuid.uuid4())
        }
        
        # Register user
        register_user(credentials)
        
        # Login user
        auth_token = login_user(credentials)
        
        # Complete tasks
        for task_index in range(7):
            update_account_status('message', f"Completing task {task_index + 1}/7 for {email}")
            complete_task(auth_token, task_index)
            time.sleep(1)
        
        # Set withdrawal address
        update_account_status('message', f"Setting withdrawal address for {email}")
        wallet = generate_wallet()
        submit_withdrawal_address(auth_token, wallet['address'])
        
        # Save account
        account_data = {
            'email': email,
            'password': password,
            'auth_token': auth_token,
            'wallet': wallet,
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        accounts.append(account_data)
        save_accounts()
        
        update_account_status('created', account_creation_status['created'] + 1)
        update_account_status('message', f"Account created: {email}")
        return account_data
    except Exception as e:
        update_account_status('failed', account_creation_status['failed'] + 1)
        update_account_status('message', f"Failed to create account: {str(e)}")
        return None

def process_accounts(count):
    """Process multiple accounts"""
    global account_creation_status
    
    for i in range(count):
        if not account_creation_status['running']:
            update_account_status('message', "Account creation stopped by user")
            break
        
        update_account_status('message', f"Processing account {i + 1}/{count}")
        
        try:
            account_data = create_account()
            if account_data:
                update_account_status('created', account_creation_status['created'] + 1)
                update_account_status('message', f"Account created: {account_data['email']}")
            else:
                update_account_status('failed', account_creation_status['failed'] + 1)
                update_account_status('message', f"Failed to create account")
        except Exception as e:
            update_account_status('failed', account_creation_status['failed'] + 1)
            update_account_status('message', f"Error: {str(e)}")
        
        if i < count - 1 and account_creation_status['running']:
            time.sleep(5)  # Wait between accounts
    
    update_account_status('running', False)
    update_account_status('message', f"Done: {account_creation_status['created']} OK, {account_creation_status['failed']} failed")
    logging.info(f"\n[+] Done: {account_creation_status['created']} OK, {account_creation_status['failed']} failed")
    logging.info(f"[*] Saved to {ACCOUNTS_FILE}")

def start_account_creation(count):
    """Start account creation process"""
    global account_creation_status
    
    # Reset status
    update_account_status('running', True)
    update_account_status('total', count)
    update_account_status('created', 0)
    update_account_status('failed', 0)
    update_account_status('message', "Starting account creation process")
    
    # Start account creation in a separate thread
    thread = threading.Thread(target=process_accounts, args=(count,))
    thread.daemon = True
    thread.start()
    
    return True

def stop_account_creation():
    """Stop account creation process"""
    global account_creation_status
    
    update_account_status('running', False)
    update_account_status('message', "Stopping account creation process...")
    
    return True

def export_accounts_to_csv():
    """Export accounts to CSV file"""
    try:
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
                    'createdAt': account.get('created_at', ''),
                    'proxy': account.get('proxy', ''),
                    'tasksCompleted': account.get('tasks_completed', 0)
                }
                writer.writerow(row)
        
        logging.info(f"[+] Accounts exported to {filename}")
        return filename
    except Exception as e:
        logging.error(f"[-] Error exporting accounts: {str(e)}")
        return None

def backup_accounts():
    """Create a backup of accounts.json"""
    try:
        if not os.path.exists(ACCOUNTS_FILE):
            logging.error(f"[-] No accounts found. Please create accounts first.")
            return None
        
        # Create backup directory if it doesn't exist
        if not os.path.exists("backups"):
            os.makedirs("backups")
        
        # Create backup file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/accounts_backup_{timestamp}.json"
        
        # Copy accounts.json to backup file
        shutil.copy2(ACCOUNTS_FILE, backup_file)
        
        logging.info(f"[+] Accounts backed up to {backup_file}")
        return backup_file
    except Exception as e:
        logging.error(f"[-] Error backing up accounts: {str(e)}")
        return None

def restore_accounts(backup_file):
    """Restore accounts from a backup"""
    try:
        if not os.path.exists(backup_file):
            logging.error(f"[-] Backup file not found: {backup_file}")
            return False
        
        # Copy backup file to accounts.json
        shutil.copy2(backup_file, ACCOUNTS_FILE)
        
        # Reload accounts
        global accounts
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
        
        logging.info(f"[+] Accounts restored from {backup_file}")
        return True
    except Exception as e:
        logging.error(f"[-] Error restoring accounts: {str(e)}")
        return False

def get_backup_files():
    """Get list of backup files"""
    try:
        if not os.path.exists("backups"):
            return []
        
        backup_files = [f for f in os.listdir("backups") if f.startswith("accounts_backup_") and f.endswith(".json")]
        
        # Sort backup files by date (newest first)
        backup_files.sort(reverse=True)
        
        return backup_files
    except Exception as e:
        logging.error(f"[-] Error getting backup files: {str(e)}")
        return []

# Initialize data
def init_data():
    """Initialize data from files"""
    global accounts, proxies, referral_code
    
    # Load referral code
    load_referral_code()
    
    # Load proxies
    proxies = load_proxies()
    
    # Load existing accounts if file exists
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                accounts = json.load(f)
            logging.info(f"[+] Loaded {len(accounts)} existing accounts from {ACCOUNTS_FILE}")
        except Exception as e:
            logging.error(f"[-] Error loading existing accounts: {str(e)}")
            accounts = []
    else:
        # Create empty accounts file if it doesn't exist
        try:
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump([], f)
            logging.info(f"[+] Created new {ACCOUNTS_FILE} file")
        except Exception as e:
            logging.error(f"[-] Error creating accounts file: {str(e)}")

# Initialize data on startup
init_data()

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        account_count = Account.query.filter_by(owner_id=current_user.id).count()
        return render_template('index.html', 
                            referral_code=current_user.referral_code,
                            account_count=account_count,
                            proxy_count=len(proxies),
                            account_creation_status=get_account_creation_status())
    else:
        return render_template('index.html', 
                            referral_code=None,
                            account_count=0,
                            proxy_count=len(proxies),
                            account_creation_status={'running': False, 'created': 0, 'failed': 0, 'total': 0, 'last_updated': ''})

@app.route('/accounts')
@login_required
def view_accounts():
    """View all accounts"""
    accounts = Account.query.filter_by(owner_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)

@app.route('/proxies')
def view_proxies():
    """View all proxies"""
    global proxies
    try:
        # Refresh proxies list before displaying
        proxies = load_proxies()
        if proxies is None:
            proxies = []
        return render_template('proxies.html', proxies=proxies)
    except Exception as e:
        logging.error(f"Error loading proxies: {str(e)}")
        flash('Error loading proxies. Please check the logs for details.', 'error')
        return render_template('proxies.html', proxies=[])

@app.route('/add_proxy', methods=['GET', 'POST'])
def add_proxy():
    """Add a proxy"""
    if request.method == 'POST':
        proxy = request.form.get('proxy', '').strip()
        
        if not proxy:
            flash('Proxy cannot be empty', 'error')
            return redirect(url_for('add_proxy'))
        
        try:
            with open(PROXIES_FILE, "a") as f:
                f.write(proxy + "\n")
            
            # Reload proxies
            global proxies
            proxies = load_proxies()
            
            flash('Proxy added successfully', 'success')
            return redirect(url_for('view_proxies'))
        except Exception as e:
            flash(f'Error adding proxy: {str(e)}', 'error')
            return redirect(url_for('add_proxy'))
    
    return render_template('add_proxy.html')

@app.route('/delete_proxy', methods=['POST'])
def delete_proxy():
    """Delete a proxy"""
    try:
        data = request.get_json()
        proxy = data.get('proxy')
        
        if not proxy:
            return jsonify({'success': False, 'message': 'No proxy provided'})
        
        # Read current proxies
        with open(PROXIES_FILE, 'r') as f:
            proxies_list = [line.strip() for line in f.readlines()]
        
        # Remove the proxy
        if proxy in proxies_list:
            proxies_list.remove(proxy)
            
            # Write back to file
            with open(PROXIES_FILE, 'w') as f:
                f.write('\n'.join(proxies_list))
            
            # Reload proxies
            global proxies
            proxies = load_proxies()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Proxy not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_proxies', methods=['POST'])
def delete_proxies():
    """Delete all proxies"""
    try:
        with open(PROXIES_FILE, "w") as f:
            f.write("")
        
        # Reload proxies
        global proxies
        proxies = load_proxies()
        
        flash('All proxies deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting proxies: {str(e)}', 'error')
    
    return redirect(url_for('view_proxies'))

@app.route('/add_referral_code', methods=['GET', 'POST'])
def add_referral_code():
    """Add a referral code"""
    if request.method == 'POST':
        code = request.form.get('referral_code', '').strip()
        
        if not code:
            flash('Referral code cannot be empty', 'error')
            return redirect(url_for('add_referral_code'))
        
        try:
            with open(REFERRAL_CODE_FILE, "w") as f:
                f.write(code)
            
            # Reload referral code
            global referral_code
            referral_code = code
            
            flash('Referral code added successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding referral code: {str(e)}', 'error')
            return redirect(url_for('add_referral_code'))
    
    return render_template('add_referral_code.html', current_code=referral_code)

@app.route('/delete_referral_code', methods=['POST'])
def delete_referral_code():
    """Delete referral code"""
    try:
        with open(REFERRAL_CODE_FILE, "w") as f:
            f.write("")
        
        # Reload referral code
        global referral_code
        referral_code = ''
        
        flash('Referral code deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting referral code: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/start_account_creation', methods=['GET', 'POST'])
@login_required
def start_account_creation_route():
    """Start account creation process"""
    if request.method == 'POST':
        count = request.form.get('count', type=int)
        use_proxies = request.form.get('use_proxies') == 'on'
        complete_tasks = request.form.get('complete_tasks') == 'on'
        set_withdrawal = request.form.get('set_withdrawal') == 'on'
        
        if not count or count <= 0:
            flash('Please enter a valid number of accounts to create', 'error')
            return redirect(url_for('start_account_creation_route'))
        
        if not current_user.referral_code:
            flash('Please set your referral code in your profile first', 'error')
            return redirect(url_for('profile'))
        
        # Initialize account creation status
        update_account_status({
            'running': True,
            'created': 0,
            'failed': 0,
            'total': count,
            'current_account': '',
            'message': 'Starting account creation...'
        })
        
        # Start account creation process
        try:
            for i in range(count):
                update_account_status({
                    'current_account': f'Creating account {i+1}/{count}',
                    'message': 'Generating credentials...'
                })
                
                credentials = create_random_email()
                proxy = get_random_proxy() if use_proxies and proxies else None
                
                try:
                    # Create account
                    account = Account(
                        username=credentials['username'],
                        email=credentials['email'],
                        password=credentials['password'],
                        device_id=credentials['deviceId'],
                        owner_id=current_user.id,
                        status='pending'
                    )
                    
                    # Register on Bilipad
                    update_account_status({'message': 'Registering account...'})
                    register_data = register_user(credentials, proxy)
                    account.user_id = register_data.get('userId')
                    
                    # Login to get auth token
                    update_account_status({'message': 'Logging in...'})
                    login_data = login_user(credentials, proxy)
                    account.auth_token = login_data.get('token')
                    
                    if complete_tasks:
                        # Complete tasks
                        update_account_status({'message': 'Completing tasks...'})
                        for task_index in range(7):
                            complete_task(account.user_id, account.auth_token, task_index, proxy)
                            account.tasks_completed = task_index + 1
                            db.session.add(account)
                            db.session.commit()
                    
                    if set_withdrawal:
                        # Generate and set wallet
                        update_account_status({'message': 'Setting up wallet...'})
                        wallet = generate_wallet()
                        account.wallet_address = wallet['address']
                        account.wallet_private_key = wallet['privateKey']
                        submit_withdrawal_address(account.user_id, wallet['address'], account.auth_token, proxy)
                    
                    account.proxy = proxy
                    account.status = 'active'
                    db.session.add(account)
                    db.session.commit()
                    
                    update_account_status({
                        'created': get_account_creation_status()['created'] + 1,
                        'message': f'Successfully created account {account.email}'
                    })
                except Exception as e:
                    update_account_status({
                        'failed': get_account_creation_status()['failed'] + 1,
                        'message': f'Error: {str(e)}'
                    })
                    logging.error(f"Error creating account: {str(e)}")
                    continue
            
            update_account_status({
                'running': False,
                'message': f'Completed: {get_account_creation_status()["created"]} created, {get_account_creation_status()["failed"]} failed'
            })
            
            flash(f'Successfully created {get_account_creation_status()["created"]} accounts', 'success')
            return redirect(url_for('view_accounts'))
        except Exception as e:
            update_account_status({
                'running': False,
                'message': f'Error: {str(e)}'
            })
            flash(f'Error creating accounts: {str(e)}', 'error')
            return redirect(url_for('start_account_creation_route'))
    
    return render_template('start_account_creation.html', proxy_count=len(proxies))

@app.route('/account_status')
@login_required
def account_status():
    """View account creation status"""
    return render_template('account_status.html', status=get_account_creation_status())

@app.route('/stop_account_creation', methods=['POST'])
@login_required
def stop_account_creation_route():
    """Stop account creation process"""
    update_account_status({
        'running': False,
        'message': 'Account creation stopped by user'
    })
    flash('Account creation stopped', 'info')
    return redirect(url_for('account_status'))

@app.route('/export_accounts', methods=['POST'])
@login_required
def export_accounts():
    """Export accounts to CSV"""
    try:
        accounts = Account.query.filter_by(owner_id=current_user.id).all()
        if not accounts:
            flash('No accounts to export', 'warning')
            return redirect(url_for('view_accounts'))

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bilipad_accounts_{timestamp}.csv'
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['email', 'password', 'userId', 'deviceId', 'authToken', 
                        'wallet_address', 'wallet_private_key', 'created_at', 
                        'proxy', 'tasks_completed']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for account in accounts:
                row = {
                    'email': account.email,
                    'password': account.password,
                    'userId': account.user_id,
                    'deviceId': account.device_id,
                    'authToken': account.auth_token,
                    'wallet_address': account.wallet_address,
                    'wallet_private_key': account.wallet_private_key,
                    'created_at': account.created_at.isoformat(),
                    'proxy': account.proxy,
                    'tasks_completed': account.tasks_completed
                }
                writer.writerow(row)
        
        flash('Accounts exported successfully', 'success')
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Error exporting accounts: {str(e)}', 'error')
    return redirect(url_for('view_accounts'))

@app.route('/backup_accounts', methods=['POST'])
def backup_accounts_route():
    """Backup accounts"""
    backup_file = backup_accounts()
    
    if backup_file:
        flash(f'Accounts backed up to {backup_file}', 'success')
    else:
        flash('Error backing up accounts', 'error')
    
    return redirect(url_for('view_accounts'))

@app.route('/restore_accounts', methods=['GET', 'POST'])
def restore_accounts_route():
    """Restore accounts from backup"""
    if request.method == 'POST':
        backup_file = request.form.get('backup_file', '')
        
        if not backup_file:
            flash('No backup file selected', 'error')
            return redirect(url_for('restore_accounts_route'))
        
        backup_path = os.path.join("backups", backup_file)
        
        if restore_accounts(backup_path):
            flash(f'Accounts restored from {backup_file}', 'success')
        else:
            flash('Error restoring accounts', 'error')
        
        return redirect(url_for('view_accounts'))
    
    backup_files = get_backup_files()
    return render_template('restore_accounts.html', backup_files=backup_files)

@app.route('/delete_accounts', methods=['POST'])
def delete_accounts():
    """Delete all accounts"""
    try:
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump([], f)
        
        # Reload accounts
        global accounts
        accounts = []
        
        flash('All accounts deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting accounts: {str(e)}', 'error')
    
    return redirect(url_for('view_accounts'))

@app.route('/api/account_status')
@login_required
def api_account_status():
    """API endpoint for getting account creation status"""
    return jsonify(get_account_creation_status())

@app.route('/api/accounts/<int:account_id>')
@login_required
def get_account_details(account_id):
    """Get account details"""
    account = Account.query.filter_by(id=account_id, owner_id=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({
        'username': account.username,
        'email': account.email,
        'status': account.status,
        'created_at': account.created_at.strftime('%Y-%m-%d %H:%M'),
        'tasks_completed': account.tasks_completed,
        'proxy': account.proxy,
        'wallet_address': account.wallet_address,
        'user_id': account.user_id,
        'device_id': account.device_id
    })

@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
@login_required
def delete_account_api(account_id):
    """Delete an account via API"""
    account = Account.query.filter_by(id=account_id, owner_id=current_user.id).first()
    if not account:
        return jsonify({'success': False, 'message': 'Account not found'})
    
    try:
        db.session.delete(account)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_account/<int:account_id>', methods=['POST'])
@login_required
def delete_account_route(account_id):
    """Delete an account via form submission"""
    account = Account.query.filter_by(id=account_id, owner_id=current_user.id).first()
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('view_accounts'))
        
    try:
        db.session.delete(account)
        db.session.commit()
        flash('Account deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'error')
    
    return redirect(url_for('view_accounts'))

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        referral_code = str(uuid.uuid4())  # Generate unique referral code

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email, referral_code=referral_code)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Use Flask-Login's login_user function
            from flask_login import login_user as flask_login_user
            flask_login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    from flask_login import logout_user as flask_logout_user
    flask_logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('profile.html')

@app.route('/update_referral', methods=['POST'])
@login_required
def update_referral():
    """Update user's referral code"""
    new_code = request.form.get('referral_code')
    if not new_code:
        flash('Referral code cannot be empty', 'error')
        return redirect(url_for('profile'))

    # Check if code is already in use by another user
    existing_user = User.query.filter(User.referral_code == new_code, User.id != current_user.id).first()
    if existing_user:
        flash('This referral code is already in use', 'error')
        return redirect(url_for('profile'))

    try:
        current_user.referral_code = new_code
        db.session.commit()
        flash('Referral code updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating referral code: {str(e)}', 'error')

    return redirect(url_for('profile'))

def get_account_creation_status():
    """Get the current account creation status"""
    global account_creation_status
    return account_creation_status

def update_account_status(status):
    """Update the account creation status"""
    global account_creation_status
    account_creation_status.update(status)
    account_creation_status['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)