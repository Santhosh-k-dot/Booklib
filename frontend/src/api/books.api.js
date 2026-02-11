import api from "./axios";

export const getBooks = () => api.get("/books");