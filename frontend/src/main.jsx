import ReactDOM from "react-dom/client"
import { createBrowserRouter, RouterProvider } from "react-router-dom"
import Root from "./routes/Root"
import ErrorPage from "./routes/ErrorPage"
import Home from "./routes/Home"
import Login from "./routes/LoginSignup"

const router = createBrowserRouter([
    {
        path: "/",
        element: <Root />,
        errorElement: <ErrorPage />,
        children: [
            {
                errorElement: <ErrorPage />,
                children: [
                    {
                        index: true,
                        element: <Home />
                    },
                    // {
                    //     path: "expense",
                    //     element: <Expense />
                    // },
                    // {
                    //     path: "overview",
                    //     element: <Overview />
                    // },
                    // {
                    //     path: "about",
                    //     element: <About />
                    // },
                    {
                        path: "login",
                        element: <Login />
                    }
                ]
            }
        ]
    }
])

ReactDOM.createRoot(document.getElementById("root")).render(<RouterProvider router={router} />)
