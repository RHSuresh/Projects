import { useNavigate } from "react-router-dom";

const Logout: React.FC = () => {

    const navigate = useNavigate();

    const handleLogout = async () => {

        try {
            const response = await fetch("http://localhost:5000/api/logout", {
                method: "POST",
                credentials: "include"
            });

            const responseData = await response.json();
            console.log(responseData.message);

            if (response.ok) {
                localStorage.clear();
                setTimeout(() => {
                    navigate("/");
                }, 1500);
            }
        }
        catch(error) {
            console.error("Logout failed: ", error);
        }
    }

    handleLogout();

    return (
        <p>Logging Out...</p>
    )
}

export default Logout
