import React, { createContext, useContext, useState, ReactNode } from "react";
import { Pet } from "./PetsList.tsx";
 
// This file watches the state of the favorites list, allows components to access the list
// Manages the state of favorite pets
interface FavInfoSpec {
  favorites: Pet[];
  addFavorite: (pet: Pet) => void;
  removeFavorite: (petId: number) => void;
}

// Create object to house favorites pet info
const FavInfo = createContext<FavInfoSpec | undefined>(
  undefined
);

// Wrap the app with a provider to hold state of favorites
export const FavoritesProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [favorites, setFavorites] = useState<Pet[]>([]);

  // Adds pet to favorites
  const addFavorite = (pet: Pet) => {
    setFavorites((prev) => [...prev, pet]);
  };

  // Removes pet from favorites
  const removeFavorite = (petId: number) => {
    setFavorites((prev) => prev.filter((pet) => pet.pet_id !== petId));
  };

  // Returns to the provider to favorites info
  return (
    <FavInfo.Provider
      value={{ favorites, addFavorite, removeFavorite }}
    >
      {children}
    </FavInfo.Provider>
  );
};

// Hook to use in the info for favorites
// Allows external components to access the favorites info
// Throws error if used outside of the provider
export const useFavorites = (): FavInfoSpec => {
  const context = useContext(FavInfo);
  if (!context) {
    throw new Error("use should be within provider");
  }
  return context;
};
