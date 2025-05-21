import React, { createContext, useContext, useState, ReactNode } from "react";
import { Pet } from "../components/PetsList.tsx";

/*define the context for favorites*/
// Manages the state of favorite pets
interface FavoritesContextType {
  favorites: Pet[];
  addFavorite: (pet: Pet) => void;
  removeFavorite: (petId: number) => void;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(
  undefined
);

export const FavoritesProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [favorites, setFavorites] = useState<Pet[]>([]);

  const addFavorite = (pet: Pet) => {
    setFavorites((prev) => [...prev, pet]);
  };

  const removeFavorite = (petId: number) => {
    setFavorites((prev) => prev.filter((pet) => pet.pet_id !== petId));
  };

  return (
    <FavoritesContext.Provider
      value={{ favorites, addFavorite, removeFavorite }}
    >
      {children}
    </FavoritesContext.Provider>
  );
};

// Custom hook to use the FavoritesContext
export const useFavorites = (): FavoritesContextType => {
  const context = useContext(FavoritesContext);
  if (!context) {
    throw new Error("useFavorites must be used within a FavoritesProvider");
  }
  return context;
};
