import { Outlet } from "react-router-dom"
import { useEffect, useState } from "react"
import axios from "axios"

export default function Root() {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(user === null);
    const [mode, setMode] = useState("dark")

    const changeMode = () => {
        mode === "dark" ? setMode("light") : setMode("dark")
    }

    useEffect(() => {
        window.matchMedia("(prefers-color-scheme: dark)")
            .addEventListener("change", event => {
                const colorScheme = event.matches ? "dark" : "light"
                console.log(colorScheme) // "dark" or "light"
                setMode(colorScheme)
            })
        if (localStorage.getItem('user')) {
            setUser(JSON.parse(localStorage.getItem('user')));
            console.log(user);
        }
    }, [])


    return (
        <div className="container" style={{
            background: mode === "dark" ? "#151515" : "#FFF5E1",
            color: mode === "dark" ? "#EEEEEE" : "#8B0000",
            
            position: "fixed",
            width: "100%",
            height: "100%",
            top: 0,
            left: 0,
            zIndex: 999,
        }}>
            <div className="content-wrapper">
                <Outlet context={{
                    user: [user, setUser],
                    login: [isLoggedIn, setIsLoggedIn]
                }} />
            </div>
        </div>
    );
}