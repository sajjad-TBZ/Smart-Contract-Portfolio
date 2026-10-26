from web3 import Web3
from solcx import compile_standard, install_solc

print("⏳ در حال آماده‌سازی...")
install_solc('0.8.0')

# ۱. کد توکن (برای استیک و جایزه)
token_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SimpleToken {
    string public name = "StakeToken";
    string public symbol = "STK";
    uint8 public decimals = 18;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    constructor(uint256 _supply) {
        balanceOf[msg.sender] = _supply * 10**uint256(decimals);
    }
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(balanceOf[msg.sender] >= _value, "Not enough balance");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        return true;
    }
    function approve(address _spender, uint256 _value) public returns (bool) {
        allowance[msg.sender][_spender] = _value;
        return true;
    }
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(balanceOf[_from] >= _value && allowance[_from][msg.sender] >= _value, "Not allowed");
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        return true;
    }
}
"""

# ۲. کد قرارداد استیکینگ
staking_source = """
pragma solidity ^0.8.0;
interface IERC20 {
    function transferFrom(address, address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
}
contract StakingContract {
    IERC20 public stakingToken;
    IERC20 public rewardToken;
    uint256 public rewardRate = 1 * 10**18; // 1 توکن جایزه به ازای هر ثانیه
    
    mapping(address => uint256) public balances;
    mapping(address => uint256) public lastUpdate;

    constructor(address _stakingToken, address _rewardToken) {
        stakingToken = IERC20(_stakingToken);
        rewardToken = IERC20(_rewardToken);
    }

    function stake(uint256 _amount) external {
        if (balances[msg.sender] > 0) {
            uint256 reward = (block.timestamp - lastUpdate[msg.sender]) * rewardRate;
            rewardToken.transfer(msg.sender, reward);
        }
        stakingToken.transferFrom(msg.sender, address(this), _amount);
        balances[msg.sender] += _amount;
        lastUpdate[msg.sender] = block.timestamp;
    }

    function withdraw() external {
        uint256 reward = (block.timestamp - lastUpdate[msg.sender]) * rewardRate;
        uint256 balance = balances[msg.sender];
        balances[msg.sender] = 0;
        lastUpdate[msg.sender] = block.timestamp;
        
        rewardToken.transfer(msg.sender, reward);
        stakingToken.transfer(msg.sender, balance);
    }
}
"""

print("⚙️ در حال کامپایل کردن قراردادها...")
compiled = compile_standard({
    "language": "Solidity",
    "sources": {"All.sol": {"content": token_source + staking_source}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
}, solc_version="0.8.0")

token_abi = compiled['contracts']['All.sol']['SimpleToken']['abi']
token_bytecode = compiled['contracts']['All.sol']['SimpleToken']['evm']['bytecode']['object']
staking_abi = compiled['contracts']['All.sol']['StakingContract']['abi']
staking_bytecode = compiled['contracts']['All.sol']['StakingContract']['evm']['bytecode']['object']

print("🔗 در حال اتصال به گاناچ...")
w3 = Web3(Web3.HTTPProvider("http://localhost:7545"))
if not w3.is_connected():
    print("❌ خطا: گاناچ باز نیست!")
    exit()

# 👇 کلید خصوصی اکانت اول 👇
private_key = "0x72ee8b37721a4b7a298487cfebbb9b04197d809fd06e2bb2a2f13841c17854b2"
account_1 = w3.eth.account.from_key(private_key)
account_2 = w3.eth.accounts[1]

# تابع کمکی اصلاح شده برای ارسال تراکنش (سازگار با Web3 نسخه ۸)
def send_tx(contract_function):
    # خود web3 کارمزد (Gas) رو به صورت اتوماتیک با سیستم جدید (EIP-1559) حساب می‌کنه
    tx = contract_function.build_transaction({
        'from': account_1.address,
        'nonce': w3.eth.get_transaction_count(account_1.address),
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=private_key)
    return w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))

print("\n🚀 در حال دیپلوی توکن‌ها...")
# دیپلوی توکن استیک (۱ میلیون)
Token = w3.eth.contract(abi=token_abi, bytecode=token_bytecode)
receipt = send_tx(Token.constructor(1000000))
stake_token_address = receipt.contractAddress
stake_token = w3.eth.contract(address=stake_token_address, abi=token_abi)

# دیپلوی توکن جایزه (۱ میلیون)
receipt = send_tx(Token.constructor(1000000))
reward_token_address = receipt.contractAddress
reward_token = w3.eth.contract(address=reward_token_address, abi=token_abi)

print(f"✅ توکن استیک: {stake_token_address}")
print(f"✅ توکن جایزه: {reward_token_address}")

print("\n🚀 در حال دیپلوی قرارداد استیکینگ...")
Staking = w3.eth.contract(abi=staking_abi, bytecode=staking_bytecode)
receipt = send_tx(Staking.constructor(stake_token_address, reward_token_address))
staking_address = receipt.contractAddress
staking_contract = w3.eth.contract(address=staking_address, abi=staking_abi)
print(f"✅ قرارداد استیکینگ: {staking_address}")

# انتقال ۱۰۰۰ توکن جایزه به قرارداد استیکینگ (تا بتونه سود بده)
print("\n💸 انتقال ۱۰۰۰ توکن جایزه به قرارداد استیکینگ...")
send_tx(reward_token.functions.transfer(staking_address, 1000 * 10**18))

# --- سناریوی استیکینگ ---
print("\n--- شروع سناریوی استیکینگ ---")
# ۱. کاربر باید به قرارداد اجازه بده که توکن‌هاش رو برداره
print("۱. دادن دسترسی به قرارداد استیکینگ (Approve)...")
send_tx(stake_token.functions.approve(staking_address, 500 * 10**18))

# ۲. استیک کردن ۵۰۰ توکن
print("۲. استیک کردن ۵۰۰ توکن...")
send_tx(staking_contract.functions.stake(500 * 10**18))

balance_staked = staking_contract.functions.balances(account_1.address).call()
print(f"✅ موجودی استیک شده: {balance_staked / 10**18} STK")

# ۳. شبیه‌سازی گذر زمان (۱۰۰ ثانیه جلو می‌ریم)
print("\n⏳ شبیه‌سازی گذر زمان (۱۰۰ ثانیه)...")
w3.provider.make_request("evm_increaseTime", [100])
w3.provider.make_request("evm_mine", [])

# ۴. برداشت پول و سود
print("۳. برداشت پول و سود...")
send_tx(staking_contract.functions.withdraw())

final_stake_balance = stake_token.functions.balanceOf(account_1.address).call()
final_reward_balance = reward_token.functions.balanceOf(account_1.address).call()

print(f"✅ موجودی نهایی STK (اصل پول): {final_stake_balance / 10**18}")
print(f"✅ موجودی نهایی Reward (سود): {final_reward_balance / 10**18}")