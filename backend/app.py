from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription

class PoseRecTrack(MediaStreamTrack):
    kind = 'video'

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        return frame

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


@app.get('/api')
def default_endpoint():
    return {'message': 'default endpoint for haichu thesis backend'}

@app.post('/api/pose')
async def handle_offer(offer: dict):
    # offer = request.json['sdp']
    try:
        pc = RTCPeerConnection()
        # processcor = PoseRec()

        @pc.on('track')
        def on_track(track):
            if track.kind == 'video':
                processed_track = PoseRecTrack(track)
                pc.addTrack(processed_track)

        remote_desc = RTCSessionDescription(sdp=offer['sdp'], type=offer['type'])
        await pc.setRemoteDescription(remote_desc)
        # Create an answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    except Exception as e:
        print('error', e)
        return {'error': e}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
