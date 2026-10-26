from web3 import Web3
from solcx import compile_standard, install_solc

print("⏳ در حال آماده‌سازی...")
install_solc('0.8.0')

# کد جدید سالیدیتی با قابلیت سوزاندن و ضرب
contract_source_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HajiCoin {
    string public name = "Haji Coin";
    string public symbol = "HAJI";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    address public owner;
    mapping(address => uint256) public balanceOf;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can do this");
        _;
    }
    
    constructor(uint256 _initialSupply) {
        owner = msg.sender;
        totalSupply = _initialSupply * 10**uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }
    
    function transfer(address _to, uint256 _value) public returns (bool success) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // قابلیت جدید ۱: سوزاندن توکن (از موجودی خودت کم میکنی و کل موجودی رو کم میکنه)
    function burn(uint256 _amount) public {
        require(balanceOf[msg.sender] >= _amount, "Not enough tokens to burn");
        balanceOf[msg.sender] -= _amount;
        totalSupply -= _amount;
        emit Transfer(msg.sender, address(0), _amount);
    }

    // قابلیت جدید ۲: ضرب توکن (فقط مالک قرارداد میتونه توکن جدید بسازه)
    function mint(address _to, uint256 _amount) public onlyOwner {
        totalSupply += _amount;
        balanceOf[_to] += _amount;
        emit Transfer(address(0), _to, _amount);
    }
}
"""

print("⚙️ در حال کامپایل کردن قرارداد...")
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"HajiCoin.sol": {"content": contract_source_code}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
}, solc_version="0.8.0")

abi = compiled_sol['contracts']['HajiCoin.sol']['HajiCoin']['abi']
bytecode = compiled_sol['contracts']['HajiCoin.sol']['HajiCoin']['evm']['bytecode']['object']

print("🔗 در حال اتصال به گاناچ...")
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    print("❌ خطا: گاناچ باز نیست!")
    exit()

# 👇 کلید خصوصی اکانت اول گاناچ رو اینجا بذار 👇
private_key = "0x72ee8b37721a4b7a298487cfebbb9b04197d809fd06e2bb2a2f13841c17854b2" 
account_1 = w3.eth.account.from_key(private_key)
account_2_address = w3.eth.accounts[1] 

print(f"👤 اکانت مالک: {account_1.address}")
print(f"👤 اکانت گیرنده: {account_2_address}")

print("\n🚀 در حال دیپلوی کردن قرارداد جدید...")
HajiCoin = w3.eth.contract(abi=abi, bytecode=bytecode)

transaction = HajiCoin.constructor(1000).build_transaction({
    'from': account_1.address,
    'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price,
    'gas': 3000000 
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"🎉 توکن ساخته شد! آدرس: {tx_receipt.contractAddress}")

my_token = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# --- تست قابلیت‌ها ---
print("\n--- تست ۱: انتقال ۱۰۰ توکن ---")
transfer_amount = 100 * 10**18
tx = my_token.functions.transfer(account_2_address, transfer_amount).build_transaction({
    'from': account_1.address, 'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price, 'gas': 100000 
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.raw_transaction))
print(f"✅ موجودی اکانت اول بعد از انتقال: {my_token.functions.balanceOf(account_1.address).call() / 10**18} HAJI")
print(f"✅ موجودی اکانت دوم: {my_token.functions.balanceOf(account_2_address).call() / 10**18} HAJI")

print("\n--- تست ۲: سوزاندن ۵۰ توکن ---")
burn_amount = 50 * 10**18
tx = my_token.functions.burn(burn_amount).build_transaction({
    'from': account_1.address, 'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price, 'gas': 100000 
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.raw_transaction))
print(f"🔥 ۵۰ توکن سوزانده شد!")
print(f"✅ موجودی جدید اکانت اول: {my_token.functions.balanceOf(account_1.address).call() / 10**18} HAJI")
print(f"✅ کل موجودی توکن در جهان: {my_token.functions.totalSupply().call() / 10**18} HAJI")

print("\n--- تست ۳: ضرب (ساخت) ۲۰۰ توکن جدید برای اکانت دوم ---")
mint_amount = 200 * 10**18
tx = my_token.functions.mint(account_2_address, mint_amount).build_transaction({
    'from': account_1.address, 'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price, 'gas': 100000 
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.raw_transaction))
print(f"✨ ۲۰۰ توکن جدید ساخته شد!")
print(f"✅ موجودی جدید اکانت دوم: {my_token.functions.balanceOf(account_2_address).call() / 10**18} HAJI")
print(f"✅ کل موجودی توکن در جهان: {my_token.functions.totalSupply().call() / 10**18} HAJI")