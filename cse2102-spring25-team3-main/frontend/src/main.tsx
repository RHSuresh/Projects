import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { FavoritesProvider } from "./components/FavoritesInfo";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <FavoritesProvider>
      <App />
    </FavoritesProvider>
  </React.StrictMode>
);
