import React, { useEffect, useState } from 'react';
import { handleError } from "./Helper.tsx";
import "../styles/adopt.css";

// interface for appointment data
interface Appointment {
    appointment_id: number;
    date: string;
    user_id: number;
    pet_id: number;
    purpose: string;
}

const BASE_URL = "http://localhost:5000";

const AppointmentsList: React.FC = () => {
    // initialize state variable to store appointment data
    const [appointments, setAppointments] = useState<Appointment[]>([]);

    // fetch all appointment made by current user
    const fetchAppointments = async () => {
        // get user id from web browser local storage
        const userId = localStorage.getItem("user_id");

        try {
            // fetch appointments from backend
            const response = await fetch(`${BASE_URL}/api/appointments/${userId}`);

            // get response data from backend
            const responseData = await response.json();
            setAppointments(responseData);

            // check for error
            if (!response.ok) {
                handleError(responseData.error,"Failed to fetch appointments");
            }

        } catch (err) {
            if (localStorage.getItem("loggedIn") === "true")
                handleError(err, "Failed to fetch appointments")
        }
    };

    // delete specific appointment made by the current user by appointment id
    const deleteAppointment = async (appointment_id: number) => {
        try {
            const response = await fetch(`${BASE_URL}/api/appointments/${appointment_id}`, {
                method: 'DELETE',
            });

            // get response data from backend
            const responseData = await response.json();

            // check for error
            if (!response.ok) {
                handleError(responseData.error, "Failed to delete appointment");
            }

            alert('Appointment deleted!');
            fetchAppointments(); // update new list

        } catch (err) {
            handleError(err, "Error deleting appointment");
        }
    };

    // fetch intial appointments
    useEffect(() => {
        fetchAppointments();
    }, []);

    // render table rows for appointment data
    const renderAppointments = () => {
        return appointments.map((app) => (
            <tr key={app.appointment_id}>
                <td>{app.appointment_id}</td>
                <td>{app.date}</td>
                <td>{app.user_id}</td>
                <td>{app.pet_id}</td>
                <td>{app.purpose}</td>
                <td>
                    <button className="user-button" onClick={() => deleteAppointment(app.appointment_id)}>
                        Delete
                    </button>
                </td>
            </tr>
        ))
    }

    /* delete appointment functionality */
    return (
        <div className="appointments-page">
            <div className="table-background">
                <h2>Scheduled Appointments</h2>
                {appointments.length === 0 ? (
                    <p>No appointments scheduled.</p>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Appointment ID</th>
                                    <th>Date</th>
                                    <th>User ID</th>
                                    <th>Pet ID</th>
                                    <th>Purpose</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                { renderAppointments() }
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AppointmentsList;
