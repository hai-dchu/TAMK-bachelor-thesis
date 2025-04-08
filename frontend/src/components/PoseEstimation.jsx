import React, { useEffect, useRef, useState } from "react";
import SimplePeer from "simple-peer/simplepeer.min.js";
import { Stream } from "readable-stream";

import "./PoseEstimation.css";
import { config } from "process";
// import Webcam from "react-webcam";

window.ReadableStream = window.ReadableStream || Stream.Readable;
window.DuplexStream = window.DuplexStream || Stream.Duplex;

const PoseEstimation = () => {
	const webcamRef = useRef(null);
	const videoRef = useRef(null);
	const [peer, setPeer] = useState(null);

	useEffect(() => {
		const startWebRTC = async () => {
			const stream = await navigator.mediaDevices.getUserMedia({ video: true });

			if (webcamRef.current) webcamRef.current.srcObject = stream;

			const p = new SimplePeer({
				initiator: true,
				trickle: false,
				stream,
				config: {
					iceServers: [
						{ urls: 'stun:stun.l.google.com:19302' }, // ok
						// {
						// 	urls: 'turn:your.turnserver.com:3478',
						// 	username: 'user',
						// 	credential: 'pass'
						// }
					]
				}
			});
			p.on("signal", async (data) => {
				console.log("SIGNAL", data);
				const response = await fetch(`${import.meta.env.VITE_BASE_URL}/pose`, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(data),
				});
				const answer = await response.json();
				console.log(answer);

				p.signal(answer);
			});

			p.on("stream", (remoteStream) => {
				if (videoRef.current) {
					videoRef.current.srcObject = remoteStream;
				}
			});

			p.on("error", (err) => {
				console.log("Error", err);
			});

			p.on('iceStateChange', (state) => {
				console.log('ICE state changed:', state);
				}
			);

			setPeer(p);
		};

		startWebRTC();
		return () => {
			peer?.destroy();
		};
	}, []);

	return (
		<div style={{
			display: "flex",
			flexDirection: "column",
			alignItems: "center",
			justifyContent: "center",
		}}>
			<video
				ref={webcamRef}
				autoPlay
				playsInline
				style={{ width: "640px", height: "480ox" }}
			/>
			<video
				ref={videoRef}
				autoPlay
				playsInline
				style={{ width: "640px", height: "480ox" }}
			/>
		</div>
	);
};

export default PoseEstimation;
