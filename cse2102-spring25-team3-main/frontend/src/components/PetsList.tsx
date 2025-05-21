import React, { useState, useEffect } from "react";
import "../styles/petslist.css"
import { useFavorites } from "./FavoritesInfo";

const BASE_URL = "http://localhost:5000";

// Pet characteristics
export interface Pet {
    pet_id: number;
    name: string;
    age: number;
    species: string;
    breed: string;
    health: string;
    temperament: string;
    notes: string;
    pictureUrl: string;
}

// Default pet information
const defaultPetInfo = {
    pet_id: 0,
    name: "",
    age: 0,
    species: "",
    breed: "",
    health: "",
    temperament: "",
    notes: "",
    pictureUrl: "",
};

// Component to display a list of pets
const PetsList: React.FC = () => {
    // Initialize state variables for pet information
    const [pets, setPets] = useState<Pet[]>([]);
    const [petInfo, setPetInfo] = useState<Pet>(defaultPetInfo);
    const { addFavorite } = useFavorites();
    const isLoggedIn = localStorage.getItem("loggedIn") === "true";

    // Initialize state variable for admin check
    const [isAdmin, setIsAdmin] = useState<boolean>(false);

    // Initialize state variables for form mode and appearance
    const [formMode, setFormMode] = useState<string>("");
    const [modalShow, setModalShow] = useState<boolean>(false);

    const openModal = () => {
        setModalShow(true);
    }

    const closeModal = () => {
        setModalShow(false);
    }

    // Initialize state variable for error checking
    const [errorMessage, setErrorMessage] = useState<string>("");

    const fetchPets = async () => {
        try {
            const response = await fetch(`${BASE_URL}/api/pets`);
            const data: Pet[] = await response.json();
            setPets(data);
        } catch (err) {
            setErrorMessage("Could not fetch pets. Please try again later.");
            console.error("Error fetching pets:", err);
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

    useEffect(() => {
        fetchPets();
        checkIsAdmin();
    }, []);

    // Display each pet with its details
    const renderPetCard = (pet: Pet) => (
        <div className="pet-card" key={pet.pet_id}>
            <h2 className="pet-name">{pet.name}</h2>
            <div className="pet-image-container">
                <img
                    src={`${BASE_URL}/${pet.pictureUrl}`}
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
            {isLoggedIn && (
                <div className="user-button-container">
                    <button
                        className="user-button"
                        onClick={() => {
                            addFavorite(pet);
                            alert(`${pet.name} added to favorites!`);
                        }}
                    >Favorite
                    </button>
                    <button
                        className="user-button"
                        onClick={() => {
                            handleAdoptPet(pet);
                        }}
                    >Adopt
                    </button>
                </div>
            )}

            {isAdmin && (
                <div className="admin-button-container">
                    <button
                        className="admin-button"
                        onClick={() => handleDeletePet(pet.pet_id)}
                    >Delete Pet
                    </button>
                    <button
                        className="admin-button"
                        onClick={() => {
                            setPetInfo(pet);
                            setFormMode("edit");
                            openModal();
                        }}
                    >Edit Pet
                    </button>
                </div>
            )}
        </div>
    );

    // Handle Input Change for Add/Edit Pet Form
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
            setPetInfo({
            ...petInfo,
            [name]: value,
        });
    };

    // Submitt application to adopt a pet
    const handleAdoptPet = async (pet: Pet) => {
        try {
            const response = await fetch(`${BASE_URL}/api/adopts`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    "pet_id": pet.pet_id,
                    "user_id": localStorage.getItem("user_id")
                }),
            });

            const responseData = await response.json();

            if (response.ok) {
                alert("Pet request sent");

            } else {
                alert('Failed to request pet.');
                console.error(`Error found while requesting pet: `, responseData.error);
            }
        }
        catch (error) {
            console.error("Error when requesting pet: ", error);
        }
    }

    // Add a new pet to the list if user is admin
    const handleAddPet = async () => {

        try {
            const response = await fetch(`${BASE_URL}/api/pets`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify(petInfo),
            });

            const responseData = await response.json();

            if (response.ok) {
                alert("New pet added successfully.");

            } else {
                alert("Failed to add new pet.");
                console.error(`Error found while adding pet: `, responseData.error);
            }
        }
        catch (error) {
            console.error("Error when adding new pet: ", error);
        }
    };

    // Delete a pet from the list if user is admin
    const handleDeletePet = async (pet_id: number) => {

        try {
            const response = await fetch(`${BASE_URL}/api/pets/${pet_id}`, {
                method: "DELETE",
                headers: {
                "Content-Type": "application/json",
                },
                credentials: "include",
            });

            const responseData = await response.json();

            if (response.ok) {
                alert(`Pet ${pet_id} deleted successfully.`);
                fetchPets();
            } else {
                alert(`Failed to delete Pet ${pet_id}`);
                console.error(`Error found while deleting pet ${pet_id}: `,responseData.error);
            }
        }
        catch (error) {
            console.error(`Error found while deleting pet ${pet_id}: `, error);
        }
    };

    // Edit pet card information
    const handleEditPet = async (pet_id: number) => {

        try {
            const response = await fetch(`${BASE_URL}/api/pets/${pet_id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify(petInfo)
            });

            const responseData = await response.json();

            if (response.ok) {
                alert(`Pet ${pet_id} updated`);
            }
            else {
                alert(`Failed to update Pet ${pet_id}`);
                console.error(`Error occured when updating Pet ${pet_id}`, responseData.error);
            }
        }
        catch (error) {
            alert(`Failed to update Pet ${pet_id}`);
            console.error(`Error occured when updating Pet ${pet_id}`, error);
        }
    };

    return (
        <div className="pets-list-page">
            {isAdmin && (<button
                className="admin-button"
                onClick={() => {
                    setPetInfo(defaultPetInfo);
                    setFormMode("add");
                    openModal();
                }}
            >Add Pet
            </button>)}
            {isAdmin && modalShow && (
                <div id="modal-container" className="modal-container">
                    <div className="modal">
                        <h2>Pet Info</h2>
                        <form onSubmit={(e) => {
                            e.preventDefault();
                            if (formMode === "add") {
                                handleAddPet();
                            }
                            else {
                                handleEditPet(petInfo.pet_id);
                            }

                            closeModal();
                        }}>
                            <div className="form-input-container">
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="name"
                                    value={petInfo.name}
                                    onChange={handleInputChange}
                                    placeholder="name"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="number"
                                    name="age"
                                    value={petInfo.age}
                                    onChange={handleInputChange}
                                    placeholder="age"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="species"
                                    value={petInfo.species}
                                    onChange={handleInputChange}
                                    placeholder="species"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="breed"
                                    value={petInfo.breed}
                                    onChange={handleInputChange}
                                    placeholder="breed"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="health"
                                    value={petInfo.health}
                                    onChange={handleInputChange}
                                    placeholder="health"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="temperament"
                                    value={petInfo.temperament}
                                    onChange={handleInputChange}
                                    placeholder="temperament"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="notes"
                                    value={petInfo.notes}
                                    onChange={handleInputChange}
                                    placeholder="notes"
                                    required
                                />
                                <input
                                    className="form-input-field"
                                    type="text"
                                    name="pictureUrl"
                                    value={petInfo.pictureUrl}
                                    onChange={handleInputChange}
                                    placeholder="pictureUrl"
                                    required
                                />
                            </div>
                            <div className="admin-button-container">
                                <button className="admin-button" onClick={ closeModal }>Cancel</button>
                                <button type="submit" className="admin-button">Submit</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            {!isLoggedIn && (
                <h2>Login to Adopt</h2>
            )}
            <h2>{pets.length} Pets Found</h2>
            {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
            <div className="pet-list-container">
                {pets.length > 0 ? (
                pets.map(renderPetCard)
                ) : (
                <p>No pets available at this moment.</p>
                )}
            </div>
        </div>
    );
};

export default PetsList;
