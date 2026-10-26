from web3 import Web3
from solcx import compile_standard, install_solc

print("⏳ در حال آماده‌سازی کامپایلر سالیدیتی (ممکنه چند لحظه طول بکشه)...")
install_solc('0.8.0')

contract_source_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 public myNumber;

    function setNumber(uint256 _newNumber) public {
        myNumber = _newNumber;
    }
}
"""

print("⚙️ در حال کامپایل کردن قرارداد...")
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"SimpleStorage.sol": {"content": contract_source_code}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
})

abi = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']
bytecode = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['evm']['bytecode']['object']

print("🔗 در حال اتصال به بلاک‌چین Ganache...")
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if w3.is_connected():
    print("✅ اتصال به Ganache با موفقیت انجام شد!")
else:
    print("❌ خطا: گاناچ باز نیست یا آدرسش اشتباهه!")
    exit()

# 👇 اینجا کلید خصوصی خودت رو از گاناچ کپی کن (با 0x شروع بشه) 👇
private_key = "0x72ee8b37721a4b7a298487cfebbb9b04197d809fd06e2bb2a2f13841c17854b2" 
account = w3.eth.account.from_key(private_key)
print(f"👤 اکانت متصل شده: {account.address}")

print("🚀 در حال ساخت و ارسال تراکنش دیپلوی...")
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.get_transaction_count(account.address)
gas_price = w3.eth.gas_price

transaction = SimpleStorage.constructor().build_transaction({
    'from': account.address,
    'nonce': nonce,
    'gasPrice': gas_price,
    'gas': 3000000 
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

print("⏳ منتظر تایید شبکه...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("\n🎉🎉🎉 تبریک! قرارداد دیپلوی شد!")
print(f"📍 آدرس قرارداد تو: {tx_receipt.contractAddress}")

# ==========================================
# تست قرارداد
# ==========================================
print("\n--- تست قرارداد با پایتون ---")
my_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

current_value = my_contract.functions.myNumber().call()
print(f"عدد فعلی ذخیره شده: {current_value}")

print("در حال تغییر عدد به 42...")
tx = my_contract.functions.setNumber(42).build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gasPrice': gas_price,
    'gas': 100000 
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
w3.eth.wait_for_transaction_receipt(tx_hash)

new_value = my_contract.functions.myNumber().call()
print(f"✅ عدد جدید ذخیره شده: {new_value}")