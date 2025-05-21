// ============================ //
// =====  Error Handling  ===== //
// ============================ //
const handleError = (err: unknown, errorMessage: string) => {
    // handles frontend error
    console.error(errorMessage, err);
    alert(`${errorMessage}: ${err}`);
};

export { handleError }

