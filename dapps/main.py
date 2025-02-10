from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3

app = FastAPI()

# Konfigurasi CORS agar Next.js bisa mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

RPC_URL = "http://127.0.0.1:8545"  # Anvil endpoint
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Smart contract address dan ABI
CONTRACT_ADDRESS = web3.to_checksum_address("0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266")
CONTRACT_ABI = [
  {
    "type": "constructor",
    "inputs": [
      {
        "name": "_message",
        "type": "string",
        "internalType": "string"
      }
    ],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "message",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "string",
        "internalType": "string"
      }
    ],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "setMessage",
    "inputs": [
      {
        "name": "_newMessage",
        "type": "string",
        "internalType": "string"
      }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  }
]


contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

@app.get("/get-message/")
def get_message():
    try:
        # Panggil fungsi "message" dari smart contract
        current_message = contract.functions.message().call()
        return {"message": current_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/set-message/")
def set_message(new_message: str):
    try:
        # Transaksi untuk memanggil fungsi "setMessage"
        tx_hash = contract.functions.setMessage(new_message).transact({"from": web3.eth.accounts[0]})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return {"status": "success", "tx_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# from fastapi import FastAPI, HTTPException
# from web3 import Web3

# app = FastAPI()

# # Provider (Gunakan node Ethereum, seperti Infura/Alchemy)
# INFURA_URL = "https://mainnet.infura.io/v3/003407eef50141a2af1c6b8b39ec0b2c"
# web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# @app.post("/verify-wallet/")
# async def verify_wallet(data: dict):
#     """
#     Verifikasi wallet signature.
#     Data yang dikirim dari frontend:
#     - address: Wallet address pengguna.
#     - message: Pesan yang ditandatangani oleh pengguna.
#     - signature: Signature dari pesan.
#     """
#     address = data.get("address")
#     message = data.get("message")
#     signature = data.get("signature")

#     if not web3.isAddress(address):
#         raise HTTPException(status_code=400, detail="Invalid wallet address")

#     try:
#         # Hash pesan sesuai dengan format EIP-191
#         message_hash = web3.sha3(text=message)
#         # Dapatkan address dari signature
#         recovered_address = web3.eth.account.recoverHash(message_hash, signature=signature)

#         # Bandingkan address yang diberikan dengan yang di-recover
#         if recovered_address.lower() == address.lower():
#             return {"status": "success", "message": "Wallet verified successfully"}
#         else:
#             raise HTTPException(status_code=401, detail="Signature verification failed")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error verifying wallet: {str(e)}")
