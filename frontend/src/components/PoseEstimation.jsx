import React, { useEffect, useRef, useState } from "react";
import SimplePeer from "simple-peer/simplepeer.min.js";
// import { Stream } from "readable-stream";

import "./PoseEstimation.css";

// window.ReadableStream = window.ReadableStream || Stream.Readable;
// window.DuplexStream = window.DuplexStream || Stream.Duplex;

const PoseEstimation = () => {
	const webcamRef = useRef(null);
	const videoRef = useRef(null);
	const [peer, setPeer] = useState(null);

	// const pc = new RTCPeerConnection();

	// pc.ontrack = event => {
	// 	if (event.streams && event.streams[0]) {
	// 		videoRef.current.srcObject = event.streams[0];
	// 	}
	// };

	// function startConnection() {
	// 	navigator.mediaDevices.getUserMedia({ video: true, audio: true })
	// 		.then(stream => {
	// 			videoRef.current.srcObject = stream;
	// 			stream.getTracks().forEach(track => pc.addTrack(track, stream));
	// 		});
	// 	// Signaling code to exchange offers/answers and candidates
	// }

	useEffect(() => {
		const startWebRTC = async () => {
			const stream = await navigator.mediaDevices.getUserMedia({ video: true });

			if (webcamRef.current) webcamRef.current.srcObject = stream;
			const response =
				await fetch("https://bghach-thesis.metered.live/api/v1/turn/credentials?apiKey=87b6b7f007fcbc21c0509ed6f3ddd1331c3b");

			// Saving the response in the iceServers array
			const iceServers = await response.json();

			const p = new SimplePeer({
				initiator: true,
				trickle: false,
				stream: stream,
				iceServers: iceServers,
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
			{/* <video
				ref={webcamRef}
				autoPlay
				playsInline
				style={{ width: "640px", height: "480px" }}
				/> */}
			<video
				ref={videoRef}
				autoPlay
				playsInline
				style={{ width: "640px", height: "480px" }}
			/>
			{/* <button onClick={startConnection}>click here</button> */}
		</div>
	);
};

export default PoseEstimation;
