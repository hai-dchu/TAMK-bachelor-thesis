from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio
from ultralytics import YOLO
import av
import cv2

import os
from dotenv import load_dotenv
load_dotenv()

model = YOLO("yolo11n-pose.pt")
test_img = cv2.imread('./test.jpg') # np.zeros((640, 480, 3), dtype=np.uint8)  # Empty black image
test_result = model(test_img)
if test_result:
    print("YOLO model loaded successfully!")
else:
    print("Warning: YOLO model failed to load!")

class PoseRecTrack(MediaStreamTrack):
    kind = 'video'

    def __init__(self, track, frame_rate=5):
        super().__init__()
        self.track = track
        self.frame_rate = frame_rate
        self.keypoints = []

    # async def recv(self):
    #     frame = await self.track.recv()
    #     return frame

    async def recv(self):
        frame = await self.track.recv()
        # img = frame.to_ndarray(format="bgr24")

        # self.frame_count += 1

        # is_left_ear_in = False
        # is_right_ear_in = False
        # is_left_shoulder_in = False
        # is_right_shoulder_in = False
        # is_left_elbow_in = False
        # is_right_elbow_in = False

        # processed_img = img
        # if self.frame_count % self.frame_rate == 0:
        #     self.frame_count = 0
        #     feed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        #     results = model(feed, verbose=False)
        #     self.keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else []

        # for kp in self.keypoints:
        #     if len(kp):
        #         is_left_ear_in = not (kp[3][0] == 0 and kp[3][1] == 0)
        #         is_right_ear_in = not (kp[4][0] == 0 and kp[4][1] == 0)
        #         is_left_shoulder_in = not (kp[5][0] == 0 and kp[5][1] == 0)
        #         is_right_shoulder_in = not (kp[6][0] == 0 and kp[6][1] == 0)
        #         is_left_elbow_in = not (kp[7][0] == 0 and kp[7][1] == 0)
        #         is_right_elbow_in = not (kp[8][0] == 0 and kp[8][1] == 0)
        #     for idx in range(len(kp)):            
        #         if idx is not None or idx in [5,6,7,8,9,10]:
        #             x,y = kp[idx]
        #             processed_img = cv2.circle(processed_img, (int(x), int(y)), 5, (0, 255, 0), -1)


        # if is_left_ear_in and is_left_shoulder_in:
        #     color = (0,0,255)
        #     x1, y1 = kp[3]
        #     x2, y2 = kp[5]
        #     upleft = (int(x2), int(y1-100))
        #     downright = (int(x2+100), int(y1))
        #     if is_left_elbow_in:
        #         x_elbow, y_elbow = kp[7]
        #         if upleft[0] < x_elbow < downright[0] and upleft[1] < y_elbow < downright[1]: # elbow inside square
        #             color = (0,255,0)
        #     processed_img = cv2.rectangle(processed_img, upleft, downright, color, 2)


        # if is_right_ear_in and is_right_shoulder_in:
        #     color = (0,0,255)
        #     x1, y1 = kp[4]
        #     x2, y2 = kp[6]
        #     upleft = (int(x2-100), int(y1-100))
        #     downright = (int(x2), int(y1))
        #     if is_right_elbow_in:
        #         x_elbow, y_elbow = kp[8]
        #         if upleft[0] < x_elbow < downright[0] and upleft[1] < y_elbow < downright[1]: # elbow inside square
        #             color = (0,255,0)
        #     processed_img = cv2.rectangle(processed_img, upleft, downright, color, 2)

        # processed_img = cv2.flip(processed_img, 1)

        # # Encode frame back
        # new_frame = av.VideoFrame.from_ndarray(processed_img, format="bgr24")

        # # Sync timestamps (important for WebRTC)
        # new_frame.pts = frame.pts
        # new_frame.time_base = frame.time_base

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
        config = RTCConfiguration(iceServers=[
                RTCIceServer(
                    urls="stun:stun.relay.metered.ca:80",
                ),
                RTCIceServer(
                    urls="turn:standard.relay.metered.ca:80",
                    username=os.getenv("TURN_SERVER_USERNAME"),
                    credential=os.getenv("TURN_SERVER_CREDENTIAL"),
                ),
                RTCIceServer(
                    urls="turn:standard.relay.metered.ca:80?transport=tcp",
                    username=os.getenv("TURN_SERVER_USERNAME"),
                    credential=os.getenv("TURN_SERVER_CREDENTIAL"),
                ),
                RTCIceServer(
                    urls="turn:standard.relay.metered.ca:443",
                    username=os.getenv("TURN_SERVER_USERNAME"),
                    credential=os.getenv("TURN_SERVER_CREDENTIAL"),
                ),
                RTCIceServer(
                    urls="turns:standard.relay.metered.ca:443?transport=tcp",
                    username=os.getenv("TURN_SERVER_USERNAME"),
                    credential=os.getenv("TURN_SERVER_CREDENTIAL"),
                ),
        ])
        pc = RTCPeerConnection(configuration=config)

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

        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)
        
        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    except Exception as e:
        print('error', e)
        return {'error': e}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
