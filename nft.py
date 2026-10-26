from web3 import Web3
from solcx import compile_standard, install_solc

print("⏳ در حال آماده‌سازی...")
install_solc('0.8.0')

# کد سالیدیتی NFT با قابلیت TokenURI (لینک به عکس و مشخصات)
contract_source_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HajiNFT {
    string public name = "Haji Art Collection";
    string public symbol = "HART";
    uint256 public totalSupply;

    mapping(uint256 => address) public ownerOf;
    mapping(address => uint256) public balanceOf;
    mapping(uint256 => address) public getApproved;
    
    // این خط جدید: ثبت لینک (Metadata) برای هر NFT
    mapping(uint256 => string) private _tokenURIs;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);

    // تابع ساخت NFT (حالا یه لینک هم به عنوان ورودی می‌گیره)
    function mint(address _to, uint256 _tokenId, string memory _uri) public {
        require(ownerOf[_tokenId] == address(0), "This Token ID is already minted!");
        ownerOf[_tokenId] = _to;
        balanceOf[_to] += 1;
        totalSupply += 1;
        _tokenURIs[_tokenId] = _uri; // ذخیره لینک عکس
        
        emit Transfer(address(0), _to, _tokenId);
    }

    // تابعی که لینک عکس رو برمی‌گردونه
    function tokenURI(uint256 _tokenId) public view returns (string memory) {
        require(ownerOf[_tokenId] != address(0), "Token does not exist");
        return _tokenURIs[_tokenId];
    }

    function transferFrom(address _from, address _to, uint256 _tokenId) public {
        require(ownerOf[_tokenId] == _from, "You are not the owner!");
        require(msg.sender == _from || getApproved[_tokenId] == msg.sender, "Not authorized!");

        balanceOf[_from] -= 1;
        balanceOf[_to] += 1;
        ownerOf[_tokenId] = _to;
        delete getApproved[_tokenId];

        emit Transfer(_from, _to, _tokenId);
    }

    function approve(address _approved, uint256 _tokenId) public {
        require(ownerOf[_tokenId] == msg.sender, "You don't own this NFT");
        getApproved[_tokenId] = _approved;
    }
}
"""

print("⚙️ در حال کامپایل کردن قرارداد NFT...")
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"HajiNFT.sol": {"content": contract_source_code}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
}, solc_version="0.8.0")

abi = compiled_sol['contracts']['HajiNFT.sol']['HajiNFT']['abi']
bytecode = compiled_sol['contracts']['HajiNFT.sol']['HajiNFT']['evm']['bytecode']['object']

print("🔗 در حال اتصال به گاناچ...")
w3 = Web3(Web3.HTTPProvider("http://localhost:7545"))

if not w3.is_connected():
    print("❌ خطا: گاناچ باز نیست!")
    exit()

# 👇 کلید خصوصی اکانت اول گاناچ رو اینجا بذار 👇
private_key = "0x72ee8b37721a4b7a298487cfebbb9b04197d809fd06e2bb2a2f13841c17854b2" 
account_1 = w3.eth.account.from_key(private_key)
account_2_address = w3.eth.accounts[1] 

print(f"👤 اکانت اول: {account_1.address}")
print(f"👤 اکانت دوم: {account_2_address}")

print("\n🚀 در حال دیپلوی کردن قرارداد NFT جدید...")
HajiNFT = w3.eth.contract(abi=abi, bytecode=bytecode)

transaction = HajiNFT.constructor().build_transaction({
    'from': account_1.address,
    'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price,
    'gas': 3000000 
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"🎉 قرارداد NFT ساخته شد! آدرس: {tx_receipt.contractAddress}")

my_nft = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# --- تست ۱: ساخت NFT با لینک عکس ---
print("\n--- تست ۱: ساخت NFT با لینک عکس (Metadata) ---")
# این یه لینک تستی IPFS هست که به یه عکس و فایل JSON اشاره می‌کنه
dummy_uri = "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/1.json"

tx1 = my_nft.functions.mint(account_1.address, 1, dummy_uri).build_transaction({
    'from': account_1.address, 'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price, 'gas': 200000 
})
signed_tx1 = w3.eth.account.sign_transaction(tx1, private_key=private_key)
w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx1.raw_transaction))

print("✅ NFT ساخته شد!")
print(f"مالک NFT: {my_nft.functions.ownerOf(1).call()}")
print(f"لینک عکس و مشخصات NFT: {my_nft.functions.tokenURI(1).call()}")

# --- تست ۲: انتقال NFT ---
print("\n--- تست ۲: انتقال NFT به اکانت دوم ---")
tx3 = my_nft.functions.transferFrom(account_1.address, account_2_address, 1).build_transaction({
    'from': account_1.address, 'nonce': w3.eth.get_transaction_count(account_1.address),
    'gasPrice': w3.eth.gas_price, 'gas': 200000 
})
signed_tx3 = w3.eth.account.sign_transaction(tx3, private_key=private_key)
w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx3.raw_transaction))

print("✅ انتقال انجام شد!")
print(f"مالک جدید NFT شماره ۱: {my_nft.functions.ownerOf(1).call()}")
print(f"لینک عکس همچنان همراه NFT هست: {my_nft.functions.tokenURI(1).call()}")