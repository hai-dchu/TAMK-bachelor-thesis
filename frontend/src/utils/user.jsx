import axios from "axios";

export const getLoggedUserInfo = async (id) => {
	const url = `${import.meta.env.VITE_BASE_URL}/users/${id}`;
	try {
		const res = await axios.get(url, {
			headers: {
				"Content-Type": "application/json",
				Authorization: `bearer ${localStorage.getItem("authToken")}`,
			},
		});
		console.log(res.data);
		return {...res.data, "token": localStorage.getItem("authToken")};
	} catch (err) {
		console.log(err);
	}
};
