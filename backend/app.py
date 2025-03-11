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

        processed_img = img
        if self.frame_count % self.frame_rate == 0:
            self.frame_count = 0
            feed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            results = model(feed)
            self.keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else []

        for kp in self.keypoints:
            for x, y in kp:
                cv2.circle(processed_img, (int(x), int(y)), 5, (0, 255, 0), -1)

        # Encode frame back
        new_frame = av.VideoFrame.from_ndarray(processed_img, format="bgr24")

        # Sync timestamps (important for WebRTC)
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame

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
                processedTrack = ProcessedVideoTrack(track, 4)

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