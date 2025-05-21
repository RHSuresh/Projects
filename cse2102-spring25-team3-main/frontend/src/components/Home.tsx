// src/components/Home.tsx
import React from "react";
import "../styles/home.css";


const Home: React.FC = () => {

    return (
        <div className="home-container">
            <header className="home-hero-image home-header-overlay">
                <h1>Pet Adoption Website</h1>
                <h2>Find the perfect pet for you</h2>
            </header>
            <section className="home-main-content">
                <div className="home-about-us">
                    <h2>About Us</h2>
                    <p>
                        We are [pet adoption center name] that specialize in helping animals in finding their new home.
                        Additionally, we feel that it is of great importance to help rescue and rehabiltate injured animals.
                        Our goal is to give every homeless animal a home and help them connect with their new families.
                    </p>
                </div>
                <div className="home-contact-container">
                    <h2>Get In Touch!</h2>
                    <div className="home-contact-card-container">
                        <div className="home-contact-card">
                            <h3>Location</h3>
                            <p>12 Canine Rd</p>
                            <p>Katzenburg, AK 3627</p>
                        </div>
                        <div className="home-contact-card">
                            <h3>Contacts</h3>
                            <p>Phone: 123-456-7890</p>
                            <p>Email: petorg@gmail.com</p>
                        </div>
                        <div className="home-contact-card">
                            <h3>Hours</h3>
                            <p>Weekdays: 8:00am - 8:00pm</p>
                            <p>Weekends: 10:00am - 8:00pm</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home;