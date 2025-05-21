import React, { useEffect, useState } from 'react';
import { handleError } from "./Helper.tsx";
import "../styles/adopt.css";

// interface for adoption application data
interface AdoptForm {
    application_id: number;
    user_id: number;
    pet_id: number;
    approval_status: string;
}

const BASE_URL = "http://localhost:5000/";

const ApplicationList: React.FC = () => {
    // Initialize state variable to store application information
    const [application, setApplication] = useState<AdoptForm[]>([]);

    // check if current user is an admin
    const [isAdmin, setIsAdmin] = useState<boolean>(false);

    // fetch all applications submitted by the current user
    const fetchApplications = async () => {
        // get user id from web browser local storage
        const userId = localStorage.getItem("user_id");

        try {
            // fetch application from backend
            const response = await fetch(`${BASE_URL}/api/adopts/${userId}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include"
            });

            // get response data from backend
            const responseData = await response.json();
            setApplication(responseData);

            // check for error
            if (!response.ok) {
                handleError(responseData.error, "Error fetching application:");
            }

        } catch (err) {
            handleError(err, "Error fetching application:");
        }
    };

    // update the approval status of an application
    const updateApplicationStatus = async (application_id: number, approval_status: string) => {
        try {
            // update application status
            const response = await fetch(`${BASE_URL}/api/adopts/${application_id}`, {
                method: 'PUT',
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    "approval_status": approval_status
                }),
            });

            // get application response data from backend
            const responseData = await response.json();

            // check for error when sending application
            if (!response.ok) {
                handleError(responseData.error, "Error updating application:");
            }

            alert('Approval Status Updated');
            fetchApplications(); // Refresh application list

        } catch (err) {
            handleError(err, "Error updating application:");
        }
    };

    // Check if the user is an admin
    const checkIsAdmin = async () => {
        try {
            const response = await fetch(`${BASE_URL}/api/login-status`, {
                method: "GET",
                credentials: "include",
            });
            const responseData = await response.json();

            if (responseData.logged_in && responseData.role === "admin") {
                setIsAdmin(true);
            }
        } catch (error) {
            console.error("Error when checking admin status: ", error);
        }
    };

    // Load the initial applications
    useEffect(() => {
        fetchApplications();
        checkIsAdmin();
    }, []);

    // render table row for each application and its columns
    const renderApplications = () => {
        return application.map((app) => (
                <tr key={app.application_id}>
                    {/* elements for each table row (columns)*/}
                    <td>{app.application_id}</td>
                    <td>{app.user_id}</td>
                    <td>{app.pet_id}</td>
                    <td>{app.approval_status}</td>
                    {isAdmin && (
                        <td>
                            <div className="act-button-container">
                                <button className="admin-button" onClick={() => updateApplicationStatus(app.application_id, "Approved")}>
                                    Approve
                                </button>
                                <button className="admin-button" onClick={() => updateApplicationStatus(app.application_id, "Denied")}>
                                    Deny
                                </button>
                            </div>
                        </td>
                    )}
                </tr>

        ))
    }

    // display all applications
    return (
        <div className="applications-page">
            <div className="table-background">
                <h2>Adoption Requests</h2>
                {application.length === 0 ? (
                    <p>No applications submitted</p>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Application ID</th>
                                    <th>User ID</th>
                                    <th>Pet ID</th>
                                    <th>Approval Status</th>
                                    {isAdmin &&(<th>Action</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                { renderApplications() }
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ApplicationList;
