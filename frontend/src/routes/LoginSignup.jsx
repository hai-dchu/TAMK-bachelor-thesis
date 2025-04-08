import React, { useRef, useState } from "react";
import axios from "axios";
import { Navigate, useOutletContext } from "react-router-dom";
import { Box, Paper, Typography, Button, TextField } from "@mui/material";
import { getLoggedUserInfo } from "../utils/user";

import "./LoginSignup.css"

const Login = () => {
	const {
        user: [user, setUser],
        login: [isLoggedIn, setIsLoggedIn],
    } = useOutletContext();
	const formRefLogin = useRef(null);
	const formRefSignup = useRef(null);
	const [loginData, setLoginData] = useState({
		email: "",
		password: "",
	});
	const [signupData, setSignupData] = useState({
		username: "",
		email: "",
		password: "",
	});
	const [login, setLogin] = useState(true);

	const handleLogin = async () => {
		const url = `${import.meta.env.VITE_BASE_URL}/auth/login`;

		try {
			const response = await axios.post(url, loginData, {
				headers: {
					"Content-Type": "application/json",
				},
			});
			console.log(response.data)
			const exp = response.data.exp * 1000 * 60 + Date.now();
			localStorage.setItem("exp", exp);
			localStorage.setItem("authToken", response.data.token);
			const loggedUserResponse = await getLoggedUserInfo(response.data.id);
			const userData = {
				id: loggedUserResponse.id,
				username: loggedUserResponse.username,
				email: loggedUserResponse.email,
				token: loggedUserResponse.token,
			};
			
			setUser(userData);
			localStorage.setItem("user", JSON.stringify(userData));
			setIsLoggedIn(true);

			setTimeout(() => {
				localStorage.removeItem("exp");
				localStorage.removeItem("authToken");
				localStorage.removeItem("user");
				setIsLoggedIn(false);
			}, exp - Date.now());

		} catch (err) {
			console.log(err);
		}
	};
	
	const handleSignup = async () => {
		const url = `${import.meta.env.VITE_BASE_URL}/users/`;
		try {
			await axios.post(url, signupData, {
				headers: {
					"Content-Type": "application/json",
				},
			});
			const response = await axios.post(
				`${import.meta.env.VITE_BASE_URL}/auth/login`,
				{
					email: signupData.email,
					password: signupData.password,
				},
			);
			localStorage.setItem("authToken", response.data.token);
			const loggedUserResponse = await getLoggedUserInfo(response.data.id);
			const userData = {
				id: loggedUserResponse.id,
				username: loggedUserResponse.username,
				email: loggedUserResponse.email,
				token: loggedUserResponse.token,
			};

			setUser(userData);
			localStorage.setItem("user", JSON.stringify(userData));
			setIsLoggedIn(true); 	
		} catch (err) {
			console.log(err);
		}
	};

	const clearForm = () => {
		setLoginData({
			email: "",
			password: "",
		});
		setSignupData({
			userName: "",
			phoneNumber: "",
			email: "",
			password: "",
		});
	};

	const handleLoginClick = () => {
		if (login) {
			if (formRefLogin.current) {
				formRefLogin.current.requestSubmit();
			}
		} else {
			setLogin(true);
		}
		clearForm();
	};

	const handleSignupClick = () => {
		if (!login) {
			if (formRefSignup.current) {
				formRefSignup.current.requestSubmit();
			}
		} else {
			setLogin(false);
		}
		clearForm();
	};

	return (user === null ? (
		<Box
			display="flex"
			justifyContent="center"
			alignItems="center"
			flexDirection="column"
			padding="10%"
		>
			<Paper
				elevation={3}
				sx={{
					padding: 3,
					borderRadius: 2,
					backgroundColor: "white",
					width: "100%",
					maxWidth: 400,
					boxShadow: 3,
				}}
			>
				{login ? (
					<div>
						<Typography variant="h5" gutterBottom align="center">
							Log in
						</Typography>
						<form
							ref={formRefLogin}
							onSubmit={(e) => {
								e.preventDefault();
								handleLogin();
							}}
						>
							<TextField
								label="Email"
								type="email"
								fullWidth
								variant="outlined"
								value={loginData.email}
								onChange={(e) =>
									setLoginData({
										email: e.target.value,
										password: loginData.password,
									})
								}
								sx={{ marginBottom: 2 }}
							/>
							<TextField
								label="Password"
								type="password"
								fullWidth
								variant="outlined"
								value={loginData.password}
								onChange={(e) =>
									setLoginData({
										email: loginData.email,
										password: e.target.value,
									})
								}
								sx={{ marginBottom: 2 }}
							/>
							<Box display="flex" justifyContent="center" mt={2}>
								<Button
									variant="contained"
									color="primary"
									onClick={handleLoginClick}
									sx={{ width: "100%" }}
								>
									Log in
								</Button>
							</Box>
						</form>
					</div>
				) : (
					<div>
						<Typography variant="h5" gutterBottom align="center">
							Sign up
						</Typography>
						<form
							ref={formRefSignup}
							onSubmit={(e) => {
								e.preventDefault();
								handleSignup();
							}}
						>
							<TextField
								label="User name"
								type="text"
								fullWidth
								variant="outlined"
								value={signupData.username}
								onChange={(e) =>
									setSignupData({
										username: e.target.value,
										email: signupData.email,
										password: signupData.password,
									})
								}
								sx={{ marginBottom: 2 }}
							/>
							<TextField
								label="Email"
								type="email"
								fullWidth
								variant="outlined"
								value={signupData.email}
								onChange={(e) =>
									setSignupData({
										username: signupData.username,
										email: e.target.value,
										password: signupData.password,
									})
								}
								sx={{ marginBottom: 2 }}
							/>
							<TextField
								label="Password"
								type="password"
								fullWidth
								variant="outlined"
								value={signupData.password}
								onChange={(e) =>
									setSignupData({
										username: signupData.username,
										email: signupData.email,
										password: e.target.value,
									})
								}
								sx={{ marginBottom: 2 }}
							/>
							<Box display="flex" justifyContent="center" mt={2}>
								<Button
									variant="contained"
									color="primary"
									onClick={handleSignupClick}
									sx={{ width: "100%" }}
								>
									Sign up
								</Button>
							</Box>
						</form>
					</div>
				)}
				<Box display="flex" justifyContent="center" mt={2}>
					<Button
						variant="outlined"
						onClick={() => setLogin(!login)}
						sx={{ width: "100%" }}
					>
						{login
							? "Don't have an account? Sign up"
							: "Already have an account? Log in"}
					</Button>
				</Box>
			</Paper>
		</Box>
	) : (
		<Navigate to="/" />
	));
};

export default Login;
