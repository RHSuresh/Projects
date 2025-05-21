// src/components/Navbar.tsx
import { Link } from 'react-router-dom';
import "../styles/nav.css";

// Navbar routes and components
const Navbar: React.FC = () => {
	return (
		<nav className="navbar">
			<Link to="/" className="nav-link">Home</Link>
			<Link to="/pets" className="nav-link">View Pets</Link>
			<Link to="/favorites" className="nav-link">Favorites</Link>
			<Link to="/appointments" className="nav-link">Appointments</Link>
			<Link to="/adopt-request" className="nav-link">Adopt Requests</Link>
			<Link to="/login" className="nav-link">Login</Link>
			<Link to="/signup" className="nav-link">Sign Up</Link>
			<Link to="/logout" className="nav-link">Logout</Link>
		</nav>
	);
};

export default Navbar;
