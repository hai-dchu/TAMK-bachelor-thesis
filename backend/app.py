from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import av
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from ultralytics import YOLO
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

model = YOLO("yolo11n-pose.pt")
test_img = cv2.imread('./test.jpg') # np.zeros((640, 480, 3), dtype=np.uint8)  # Empty black image
test_result = model(test_img)
if test_result:
    print("YOLO model loaded successfully!")
else:
    print("Warning: YOLO model failed to load!")

pcs = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown cleanup"""
    yield  # This runs while the app is running
    print("Shutting down: Closing all WebRTC connections...")
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    print("Shutdown complete.")


class ProcessedVideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, frame_rate=15):
        super().__init__()
        self.track = track
        self.frame_count = 0
        self.frame_rate = frame_rate
        self.keypoints = []

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        self.frame_count += 1

        is_left_ear_in = False
        is_right_ear_in = False
        is_left_shoulder_in = False
        is_right_shoulder_in = False
        is_left_elbow_in = False
        is_right_elbow_in = False

        processed_img = img
        # if self.frame_count % self.frame_rate == 0:
        #     self.frame_count = 0
        #     feed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        #     results = model(feed, verbose=False)
        #     keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else []

        # for kp in keypoints:
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

        # Encode frame back
        new_frame = av.VideoFrame.from_ndarray(processed_img, format="bgr24")

        # Sync timestamps (important for WebRTC)
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame

@app.get("/api")
async def hello_world():
    return {"message": "Hello World"}

@app.post("/api/pose")
async def offer(offer: dict):
    try:
        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("track")
        def on_track(track):
            print(f"Received track: {track.kind}")
            if track.kind == "video":
                print("Processing video track")
                processedTrack = ProcessedVideoTrack(track, 6)

                pc.addTrack(processedTrack)

        remote_description = RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
        await pc.setRemoteDescription(remote_description)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)

        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    except Exception as e:
        print(f"error in offer(): {e}")
        return {"error": str(e)}


from routes.users import router as users_router
from routes.auth import router as auth_router

app.include_router(users_router)
app.include_router(auth_router)