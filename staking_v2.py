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

# ۲. کد پیشرفته قرارداد استیکینگ (با استانداردهای امنیتی)
staking_source = """
pragma solidity ^0.8.0;

interface IERC20 {
    function transferFrom(address, address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}

contract AdvancedStaking {
    IERC20 public stakingToken;
    IERC20 public rewardToken;
    
    uint256 public rewardRate; 
    address public owner;
    bool private locked;

    mapping(address => uint256) public balances;
    mapping(address => uint256) public lastUpdate;

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount, uint256 reward);
    event EmergencyWithdrawn(address indexed user, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    modifier nonReentrant() {
        require(!locked, "No reentrancy");
        locked = true;
        _;
        locked = false;
    }

    constructor(address _stakingToken, address _rewardToken, uint256 _initialRate) {
        stakingToken = IERC20(_stakingToken);
        rewardToken = IERC20(_rewardToken);
        rewardRate = _initialRate;
        owner = msg.sender;
    }

    /// @notice تنظیم مجدد نرخ سود (فقط توسط مالک قرارداد)
    function setRewardRate(uint256 _newRate) external onlyOwner {
        rewardRate = _newRate;
    }

    /// @notice استیک کردن توکن‌ها و دریافت سود معوقه
    function stake(uint256 _amount) external nonReentrant {
        require(_amount > 0, "Cannot stake 0");
        
        if (balances[msg.sender] > 0) {
            uint256 reward = (block.timestamp - lastUpdate[msg.sender]) * rewardRate;
            if (reward > 0) {
                require(rewardToken.transfer(msg.sender, reward), "Reward transfer failed");
            }
        }
        
        require(stakingToken.transferFrom(msg.sender, address(this), _amount), "Stake transfer failed");
        balances[msg.sender] += _amount;
        lastUpdate[msg.sender] = block.timestamp;
        
        emit Staked(msg.sender, _amount);
    }

    /// @notice برداشت اصل پول و سود
    function withdraw() external nonReentrant {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "Nothing to withdraw");
        
        uint256 reward = (block.timestamp - lastUpdate[msg.sender]) * rewardRate;
        
        balances[msg.sender] = 0;
        lastUpdate[msg.sender] = block.timestamp;

        if (reward > 0) {
            require(rewardToken.transfer(msg.sender, reward), "Reward transfer failed");
        }
        require(stakingToken.transfer(msg.sender, balance), "Stake transfer failed");

        emit Withdrawn(msg.sender, balance, reward);
    }

    /// @notice برداشت اضطراری فقط اصل پول بدون سود (برای مواقع ضروری)
    function emergencyWithdraw() external nonReentrant {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "Nothing to withdraw");
        
        balances[msg.sender] = 0;
        lastUpdate[msg.sender] = block.timestamp;
        require(stakingToken.transfer(msg.sender, balance), "Transfer failed");

        emit EmergencyWithdrawn(msg.sender, balance);
    }

    /// @notice مشاهده سود محاسبه شده فعلی کاربر
    function earned(address _account) external view returns (uint256) {
        if (balances[_account] == 0) return 0;
        return (block.timestamp - lastUpdate[_account]) * rewardRate;
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
staking_abi = compiled['contracts']['All.sol']['AdvancedStaking']['abi']
staking_bytecode = compiled['contracts']['All.sol']['AdvancedStaking']['evm']['bytecode']['object']

print("🔗 در حال اتصال به گاناچ...")
w3 = Web3(Web3.HTTPProvider("http://localhost:7545"))
if not w3.is_connected():
    print("❌ خطا: گاناچ باز نیست!")
    exit()

# 👇 کلید خصوصی اکانت اول 👇
private_key = "0x4fb93c7b8c46ccf394ab73e2fbfb30f437b192ca46c3681484e91edbed9a0c23"
account_1 = w3.eth.account.from_key(private_key)

# تابع کمکی برای ارسال تراکنش
def send_tx(contract_function):
    tx = contract_function.build_transaction({
        'from': account_1.address,
        'nonce': w3.eth.get_transaction_count(account_1.address),
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=private_key)
    return w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))

print("\n🚀 در حال دیپلوی توکن‌ها...")
Token = w3.eth.contract(abi=token_abi, bytecode=token_bytecode)
receipt = send_tx(Token.constructor(1000000))
stake_token_address = receipt.contractAddress
stake_token = w3.eth.contract(address=stake_token_address, abi=token_abi)

receipt = send_tx(Token.constructor(1000000))
reward_token_address = receipt.contractAddress
reward_token = w3.eth.contract(address=reward_token_address, abi=token_abi)

print("\n🚀 در حال دیپلوی قرارداد استیکینگ پیشرفته...")
Staking = w3.eth.contract(abi=staking_abi, bytecode=staking_bytecode)
# نرخ اولیه: 1 توکن در ثانیه (1 * 10**18)
receipt = send_tx(Staking.constructor(stake_token_address, reward_token_address, 10**18))
staking_address = receipt.contractAddress
staking_contract = w3.eth.contract(address=staking_address, abi=staking_abi)
print(f"✅ قرارداد استیکینگ پیشرفته: {staking_address}")

print("\n💸 انتقال ۱۰۰۰ توکن جایزه به قرارداد استیکینگ...")
send_tx(reward_token.functions.transfer(staking_address, 1000 * 10**18))

print("\n--- شروع تست سناریوها ---")
print("۱. دادن دسترسی (Approve)...")
send_tx(stake_token.functions.approve(staking_address, 500 * 10**18))

print("۲. استیک کردن ۵۰۰ توکن...")
send_tx(staking_contract.functions.stake(500 * 10**18))
print(f"✅ موجودی استیک شده: {staking_contract.functions.balances(account_1.address).call() / 10**18} STK")

print("\n⏳ شبیه‌سازی گذر زمان (۱۰۰ ثانیه)...")
w3.provider.make_request("evm_increaseTime", [100])
w3.provider.make_request("evm_mine", [])

# تست تابع earned (محاسبه سود قبل از برداشت)
earned_reward = staking_contract.functions.earned(account_1.address).call()
print(f"💰 سود محاسبه شده در این لحظه: {earned_reward / 10**18} Reward")

print("\n۳. برداشت اصل پول و سود...")
send_tx(staking_contract.functions.withdraw())

final_stake = stake_token.functions.balanceOf(account_1.address).call()
final_reward = reward_token.functions.balanceOf(account_1.address).call()

print(f"✅ موجودی نهایی STK (اصل پول): {final_stake / 10**18}")
print(f"✅ موجودی نهایی Reward (سود): {final_reward / 10**18}")