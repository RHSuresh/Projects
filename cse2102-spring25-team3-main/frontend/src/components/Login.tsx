import React, {useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";
import { handleError } from "./Helper.tsx"
import "../styles/auth.css";

const BASE_URL = "http://localhost:5000";

const Login: React.FC = () => {

    // Initialize state variables for form inputs
    const [usernameOrEmail, setUsernameOrEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");

    // Initialize state variable for form submission
    const [isSubmittingForm, setIsSubmittingForm] = useState(false);

    // a react Router Hook, connects to other routes
    const navigate = useNavigate();

    // a react Hook that runs after component finish rendering
    useEffect(() => {
        // define function to check login status, async means that it does not wait for fetch to finish before going on to do other tasks
        const checkLoginStatus = async () => {
            try {
                // fetch login status from backend
                const response = await fetch(`${BASE_URL}/api/login-status`, {
                    method: "GET",
                    credentials: "include" // send cookie data to backend
                });
                // wait for response from backend
                const responseData = await response.json();
                // check if the user is logged in based on backend response
                if (responseData.logged_in) {
                    navigate("/"); // direct user to home page for now may change later to pet search page instead
                }
            } catch (err) {
                handleError(err, "Login status check failed");
            }
        };
        checkLoginStatus();
    }, [navigate]);

    // function to handle form submission and send user data to the backend
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); // prevent page reload when clicking SignUp button
        setIsSubmittingForm(true); // prevent user from spamming submit button

        // Check all fields entered, condition is checked in backend but provides extra safety measures
        if (!usernameOrEmail || !password) {
            handleError("Username or Password Missing", "All fields are required");
            setIsSubmittingForm(false);
            return;
        }

        // user data to send to backend
        const userData = {
            username_or_email: usernameOrEmail,
            password: password
        }

        try {
            // send data to and fetch reponse from backend
            // inside the fetch, is the route used to connect to the backend
            //  - Before connecting to the Cloud it starts with : http://127.0.0.1:5000
            //  - Change it after connecting to Cloud
            const response = await fetch(`${BASE_URL}/api/login`, {
                // POST - send data from client (frontend) to server (backend)
                // Content-Type: application/json - backend is expecting data as json formatted string
                // body - convert the data being sent to json formatted string
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData),
                credentials: "include"
            });

            // get response data from backend
            const responseData = await response.json();

            // check response after login attempt
            if (response.ok) {
                alert("Login Success");
                // save user credentials in Web Browser local storage
                localStorage.setItem("role", JSON.stringify(responseData.role));
                localStorage.setItem("user_id", JSON.stringify(responseData.user_id));
                localStorage.setItem("loggedIn", "true");

                // stall for some time before directing
                setTimeout(() => {
                    navigate("/");
                }, 1000);
                console.log(responseData);
            }
            else {
                handleError(responseData.error, "Login Failed");
            }
        }
        catch (err) {
            handleError(err, "Login Failed");
        }
        finally {
            setIsSubmittingForm(false);
        }
    };

    // navigate to signup page
    const gotoSignUp = async () => {
        setTimeout(() => {
            navigate("/signup");
        }, 250);
    }

    return (
        <div className="auth-container">
            <h2 className="auth-header">Login</h2>
            {/* triggers handleSubmit function when submitted */}
            <form onSubmit={handleSubmit} className="auth-form">
                <input
                    className="auth-input-field"
                    // type is a text
                    type="text"
                    // display the current value of username - intially will be empty
                    value={usernameOrEmail}
                    // e - an event object
                    // e.target - the element that triggered the event, in this case is the input element
                    // e.target.value - the value in the input element
                    onChange={(e) => setUsernameOrEmail(e.target.value)}
                    placeholder="username or email"
                />
                <input
                    className="auth-input-field"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="password"
                />
                {/* form is submitted when button is clicked, will trigger handleSubmit function */}
                <button type="submit" disabled={isSubmittingForm} className="auth-submit-button">
                    LOGIN
                </button>
            </form>
            <p className="auth-link-paragraph">Need an account?
                <a onClick={gotoSignUp} className="auth-link"> SIGN UP</a>
            </p>
        </div>
    )
};

export default Login
