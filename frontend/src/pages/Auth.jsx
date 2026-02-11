import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Checkbox,
  FormControlLabel,
  Link,
  InputAdornment,
} from "@mui/material";
import {
  PersonOutline,
  LockOutlined,
  EmailOutlined,
} from "@mui/icons-material";
import { loginUser, registerUser } from "../api/auth.api";
import { useNavigate } from "react-router-dom";

export default function Auth({ isLogin: initialIsLogin }) {
  const [isLogin, setIsLogin] = useState(initialIsLogin);
  const navigate = useNavigate(); // ✅ ADD THIS
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    email: "",
    full_name: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = isLogin
        ? await loginUser(formData)
        : await registerUser(formData);

      if (isLogin) {
        localStorage.setItem("token", res.data.access_token);
        navigate("/home"); // ✅ THIS is the key line
      }

      alert(isLogin ? "Welcome back!" : "Account created!");
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || "Something went wrong"));
    }
  };
  return (
    <Box
      sx={{
        display: "flex",
        width: "100vw", // Forces the container to be 100% of the viewport width
        minHeight: "100vh",
        overflow: "hidden",
        margin: 0, // Removes any default browser padding
        padding: 0,
      }}
    >
      {/* LEFT SIDE - 75% - Purple Gradient with Decorative Elements */}
      <Box
        sx={{
          width: "75%",
          background: "linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)",
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
        }}
      >
        {/* Decorative diagonal stripes */}
        <Box
          sx={{
            position: "absolute",
            width: "200px",
            height: "500px",
            background: "linear-gradient(135deg, #F97316 0%, #F59E0B 100%)",
            borderRadius: "60px",
            transform: "rotate(45deg)",
            left: "15%",
            top: "20%",
            opacity: 0.8,
          }}
        />
        <Box
          sx={{
            position: "absolute",
            width: "180px",
            height: "450px",
            background: "linear-gradient(135deg, #F97316 0%, #F59E0B 100%)",
            borderRadius: "60px",
            transform: "rotate(45deg)",
            left: "25%",
            top: "30%",
            opacity: 0.6,
          }}
        />
        <Box
          sx={{
            position: "absolute",
            width: "150px",
            height: "400px",
            background: "linear-gradient(135deg, #F97316 0%, #F59E0B 100%)",
            borderRadius: "50px",
            transform: "rotate(45deg)",
            left: "10%",
            top: "40%",
            opacity: 0.7,
          }}
        />
        <Box
          sx={{
            position: "absolute",
            width: "120px",
            height: "350px",
            background: "linear-gradient(135deg, #F97316 0%, #F59E0B 100%)",
            borderRadius: "50px",
            transform: "rotate(45deg)",
            left: "5%",
            top: "55%",
            opacity: 0.5,
          }}
        />

        {/* Text Content */}
        <Box sx={{ position: "relative", zIndex: 1, maxWidth: "600px", px: 6 }}>
          <Typography
            variant="h2"
            sx={{
              color: "white",
              fontWeight: 700,
              mb: 3,
              fontSize: { xs: "2.5rem", md: "3.5rem" },
            }}
          >
            Library Management System
          </Typography>
          <Typography
            sx={{
              color: "rgba(255, 255, 255, 0.9)",
              fontSize: "1.1rem",
              lineHeight: 1.8,
            }}
          >
            Welcome to our comprehensive library management system. Manage your
            books, track borrowings, and explore our vast collection of
            resources. Access thousands of books, journals, and digital
            resources at your fingertips.
          </Typography>
        </Box>
      </Box>

      {/* RIGHT SIDE - 25% - Login/Register Form */}
      <Box
        sx={{
          width: "25%",
          backgroundColor: "#FAFAFA",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          px: 3,
          py: 4,
        }}
      >
        <Box sx={{ width: "100%", maxWidth: "350px" }}>
          {/* Header */}
          <Typography
            sx={{
              color: "#A78BFA",
              fontSize: "0.875rem",
              fontWeight: 600,
              letterSpacing: "0.1em",
              mb: 4,
              textAlign: "center",
            }}
          >
            {isLogin ? "USER LOGIN" : "CREATE ACCOUNT"}
          </Typography>

          <Box component="form" onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Full Name"
                  value={formData.full_name}
                  onChange={(e) =>
                    setFormData({ ...formData, full_name: e.target.value })
                  }
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "white",
                      borderRadius: "8px",
                      fontSize: "0.9rem",
                      "& fieldset": {
                        borderColor: "#E5E7EB",
                      },
                      "&:hover fieldset": {
                        borderColor: "#C4B5FD",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "#A78BFA",
                      },
                    },
                  }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonOutline
                          sx={{ color: "#A78BFA", fontSize: "1.2rem" }}
                        />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "white",
                      borderRadius: "8px",
                      fontSize: "0.9rem",
                      "& fieldset": {
                        borderColor: "#E5E7EB",
                      },
                      "&:hover fieldset": {
                        borderColor: "#C4B5FD",
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "#A78BFA",
                      },
                    },
                  }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailOutlined
                          sx={{ color: "#A78BFA", fontSize: "1.2rem" }}
                        />
                      </InputAdornment>
                    ),
                  }}
                />
              </>
            )}

            <TextField
              fullWidth
              variant="outlined"
              placeholder="Username"
              value={formData.username}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
              sx={{
                mb: 2,
                "& .MuiOutlinedInput-root": {
                  backgroundColor: "white",
                  borderRadius: "8px",
                  fontSize: "0.9rem",
                  "& fieldset": {
                    borderColor: "#E5E7EB",
                  },
                  "&:hover fieldset": {
                    borderColor: "#C4B5FD",
                  },
                  "&.Mui-focused fieldset": {
                    borderColor: "#A78BFA",
                  },
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonOutline
                      sx={{ color: "#A78BFA", fontSize: "1.2rem" }}
                    />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              variant="outlined"
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              sx={{
                mb: 2,
                "& .MuiOutlinedInput-root": {
                  backgroundColor: "white",
                  borderRadius: "8px",
                  fontSize: "0.9rem",
                  "& fieldset": {
                    borderColor: "#E5E7EB",
                  },
                  "&:hover fieldset": {
                    borderColor: "#C4B5FD",
                  },
                  "&.Mui-focused fieldset": {
                    borderColor: "#A78BFA",
                  },
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockOutlined
                      sx={{ color: "#A78BFA", fontSize: "1.2rem" }}
                    />
                  </InputAdornment>
                ),
              }}
            />

            {isLogin && (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2.5,
                }}
              >
                <FormControlLabel
                  control={
                    <Checkbox
                      size="small"
                      sx={{
                        color: "#A78BFA",
                        "&.Mui-checked": {
                          color: "#A78BFA",
                        },
                      }}
                    />
                  }
                  label={
                    <Typography sx={{ fontSize: "0.8rem", color: "#6B7280" }}>
                      Remember
                    </Typography>
                  }
                />
                <Link
                  href="#"
                  underline="hover"
                  sx={{
                    fontSize: "0.8rem",
                    color: "#A78BFA",
                  }}
                >
                  Forgot?
                </Link>
              </Box>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{
                background: "linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)",
                color: "white",
                py: 1.3,
                borderRadius: "25px",
                textTransform: "uppercase",
                fontWeight: 600,
                fontSize: "0.85rem",
                letterSpacing: "0.05em",
                boxShadow: "0 4px 15px rgba(139, 92, 246, 0.4)",
                mb: 2,
                "&:hover": {
                  background:
                    "linear-gradient(135deg, #7C3AED 0%, #DB2777 100%)",
                  boxShadow: "0 6px 20px rgba(139, 92, 246, 0.5)",
                },
              }}
            >
              {isLogin ? "LOGIN" : "CREATE ACCOUNT"}
            </Button>

            {/* Toggle between Login and Register */}
            <Box sx={{ textAlign: "center" }}>
              <Typography sx={{ fontSize: "0.85rem", color: "#6B7280", mb: 1 }}>
                {isLogin
                  ? "Don't have an account?"
                  : "Already have an account?"}
              </Typography>
              <Link
                component="button"
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                underline="hover"
                sx={{
                  fontSize: "0.875rem",
                  color: "#A78BFA",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                {isLogin ? "Create New Account" : "Login Here"}
              </Link>
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
