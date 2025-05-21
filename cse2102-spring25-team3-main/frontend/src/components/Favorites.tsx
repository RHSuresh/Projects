import React, { useState } from 'react';
import { useFavorites } from './FavoritesInfo';
import { Pet } from './PetsList';
import { handleError } from './Helper.tsx';
import "../styles/petslist.css";

const BASE_URL = "http://localhost:5000";

const Favorites: React.FC = () => {
    const { favorites, removeFavorite } = useFavorites();
    const [selectedPet, setSelectedPet] = useState<Pet | null>(null);
    const [selectedTime, setSelectedTime] = useState('');
    const [availableTimes, setAvailableTimes] = useState<string[]>([]);

    // Create time slots (depending on day)
    const generateTimeSlots = () => {
        const now = new Date();
        const isWeekend = now.getDay() === 0 || now.getDay() === 6; // Sunday=0, Saturday=6
        const slots: string[] = [];
        const startHour = isWeekend ? 10 : 8;
        const endHour = 20; // 8PM

        for (let hour = startHour; hour <= endHour; hour++) {
            const timeString = `${hour}:00`;
            slots.push(timeString);
        }
        return slots;
    };

    /*Open schedule popup and generate time slots*/
    const openSchedule = (pet: Pet) => {
        setSelectedPet(pet);
        setAvailableTimes(generateTimeSlots());
    };

    // Confirm appointment and send to backend
    // Check if pet and time are selected, then sends to backend
    const confirmAppointment = async () => {
        if (!selectedPet || !selectedTime) {
            handleError("Please select a time", "No time selected");
            return;
        }

        try {
            // current date
            const today = new Date().toISOString().split('T')[0];

            const response = await fetch(`${BASE_URL}/api/appointments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: localStorage.getItem("user_id"),
                    pet_id: selectedPet.pet_id,
                    date: today,
                    purpose: `Appointment at ${selectedTime}`,
                }),
            })

            if (!response.ok) {

                const errorText = await response.text();
                throw new Error(`Failed to schedule appointment: ${errorText}`);
            }

            // Wait for response to be returned, send alert to user of scheduled appointment
            await response.json();
            alert(`Appointment for ${selectedPet.name} scheduled at ${selectedTime}!`);
            setSelectedPet(null);
            setSelectedTime('');
        } catch (err) {
            handleError(err, "Failed to schedule appointment");
        }
    };

    return (
        // Shows pet list page frontend
        <div className="pets-list-page">
            <h2>Favorited Pets</h2>
            {favorites.length === 0 ? (
                <p>No pets favorited.</p>
            ) : (
                <div className="pet-list-container">
                    {favorites.map((pet) => (
                        <div className="pet-card" key={pet.pet_id}>
                            <h2 className="pet-name">{pet.name}</h2>
                            <div className="pet-image-container">
                                <img
                                    src={`${BASE_URL}${pet.pictureUrl}`}
                                    alt={pet.name}
                                    className="pet-image"
                                    onError={(e) => {
                                        const image = e.target as HTMLImageElement;
                                        image.src = pet.pictureUrl;
                                    }}
                                />
                            </div>
                            <div className="pet-info">
                                <p>ID: { pet.pet_id }</p>
                                <p>Age: { pet.age }</p>
                                <p>Species: { pet.species }</p>
                                <p>Breed:{ pet.breed }</p>
                                <p>Temperament: { pet.temperament }</p>
                                <p>Health: { pet.health }</p>
                                <p>Notes: {pet.notes}</p>
                            </div>
                            <button className="user-button" onClick={() => removeFavorite(pet.pet_id)}>Remove</button>
                            <button className="user-button" onClick={() => openSchedule(pet)}>Schedule Appointment</button>
                        </div>
                    ))}
                </div>
            )}

            {/* Popup for scheduling */}
            {selectedPet && (
                <div className="modal-container">
                    <div className="modal">
                        <h3>Schedule Appointment for {selectedPet.name}</h3>
                        <div className="form-input-container">
                            <select
                                className="form-input-field"
                                value={selectedTime}
                                onChange={(e) => setSelectedTime(e.target.value)}
                            >
                                <option value="">Select a time</option>
                                {availableTimes.map((time) => (
                                    <option key={time} value={time}>{time}</option>
                                ))}
                            </select>
                        </div>
                        <div className="admin-button-container">
                            <button className="user-button" onClick={confirmAppointment}>Confirm Appointment</button>
                            <button className="user-button" onClick={() => { setSelectedPet(null); setSelectedTime(''); }}>
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Favorites;
