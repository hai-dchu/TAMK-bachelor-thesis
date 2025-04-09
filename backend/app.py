from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from flask import Flask, request, jsonify
from flask_sockets import Sockets

# app = Flask(__name__)
# sockets = Sockets(app)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

from aiortc import RTCPeerConnection, MediaStreamTrack

@app.route('/api/pose', methods=['POST'])
def handle_offer():
    offer = request.json['sdp']
    pc = RTCPeerConnection()
    pc.setRemoteDescription(offer)
    # Create an answer
    answer = pc.createAnswer()
    pc.setLocalDescription(answer)
    return jsonify({'sdp': pc.localDescription.sdp})


# @sockets.route('/websocket')
# def echo_socket(ws):
#     while not ws.closed:
#         message = ws.receive()
#         ws.send(message)  # Echo the websocket message back to the client

if __name__ == "__main__":
    app.run()
