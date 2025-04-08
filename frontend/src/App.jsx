import { useState, useEffect } from "react";

import "./App.css";
import PoseEstimation from "./components/PoseEstimation";
import Login from "./components/LoginSignup";

function App() {
	const [user, setUser] = useState(JSON.parse(localStorage.getItem("user")) || null);
	const [isLoggedIn, setIsLoggedIn] = useState(false);

	useEffect(() => {		
		if (user) {
			setIsLoggedIn(true);
		}
	}, [user])
	return (
		<>
			{/* <PoseEstimation /> */}
			{isLoggedIn && user ? (
				<div style={{
					display: "flex",
					alignItems: "center",
					justifyContent: "center",
					flexDirection: "column"
				}}>
					{/* <PoseEstimation /> */}
					<p>Logged in as {user.username}</p>
				</div>
			) : (
				<Login setUser={setUser} setIsLoggedIn={setIsLoggedIn} />
			)}
		</>
	);
}

export default App;
