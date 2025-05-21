import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/auth.css"
import { handleError } from "./Helper";

const BASE_URL = "http://localhost:5000";

// SignUp component using React.FC
const SignUp: React.FC = () => {

    // Initialize state variables for form inputs
    const [username, setUsername] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [email, setEmail] = useState<string>("");

    // Initialize state variable for form submission
    const [isSubmittingForm, setIsSubmittingForm] = useState<boolean>(false);

    // a react Router Hook, connects to other routes
    const navigate = useNavigate();

    // function to handle form submission and send user data to the backend
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); // prevent page reload when clicking SignUp button

        setIsSubmittingForm(true); // prevent user from spamming submit button

        // Check all fields entered, condition is checked in backend but provides extra safety measures
        if (!username || !email || !password) {
            handleError("All fields are required", "Registration Failed");
            setIsSubmittingForm(false);
            return;
        }

        // data to send to backend
        const userData = {
            username: username,
            email: email,
            password: password
        }

        try {
            // send data to and fetch reponse from backend
            // inside the fetch, is the route used to connect to the backend
            //  - Before connecting to the Cloud it starts with : http://127.0.0.1:5000
            //  - Change it after connecting to Cloud
            const response = await fetch(`${BASE_URL}/api/users`, {
                // POST - send data from client (frontend) to server (backend)
                // Content-Type: application/json - backend is expecting data as json formatted string
                // body - convert the data being sent to json formatted string
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData)
            });

            // get response from backend
            const responseData = await response.json();

            // check response after signup response
            if (response.ok) {
                alert("Sign Up Successful");
                // stall for some time before directing
                setTimeout(() => {
                    navigate("/login");
                }, 2000);
            }
            else {
                handleError(responseData.error, "Sign Up Failed");
            }
        }
        catch (error) {
            handleError(error, "Sign Up Failed");
        }
    }

    // direct user to login page
    const gotoLogin = async () => {
        setTimeout(() => {
            navigate("/login");
        }, 250);
    }

    return (
        <div className="auth-container">
            <h2 className="auth-header">Sign Up</h2>
            {/* triggers handleSubmit function when submitted */}
            <form onSubmit={handleSubmit} className="auth-form">
                <input
                    className="auth-input-field"
                    // type is a text
                    type="text"
                    // display the current value of username - intially will be empty
                    value={username}
                    // e - an event object
                    // e.target - the element that triggered the event, in this case is the input element
                    // e.target.value - the value in the input element
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="username"
                />
                <input
                    className="auth-input-field"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="email"
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
                    Sign Up
                </button>
            </form>
            <p>Already a user?
                <a onClick={gotoLogin} className="auth-link"> Login</a>
            </p>
        </div>
    );
};

export default SignUp;
