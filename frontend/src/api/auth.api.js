import api from "./axios";

export const loginUser = (data) => {
  return api.post("/login", {
    username: data.username,
    password: data.password,
  });
};

export const registerUser = (data) => {
  return api.post("/register", {
    username: data.username,
    password: data.password,
    email: data.email,
    full_name: data.full_name,
  });
};