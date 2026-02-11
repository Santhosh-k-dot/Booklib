import { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  InputAdornment,
  Chip,
  IconButton,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import LogoutIcon from "@mui/icons-material/Logout";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import { getBooks } from "../api/books.api";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [books, setBooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  const DEFAULT_BOOK_IMG =
    "https://images.unsplash.com/photo-1556566952-11eff3d06ed4?w=600&auto=format&fit=crop&q=60";

  useEffect(() => {
    const loadBooks = async () => {
      try {
        const res = await getBooks();
        setBooks(res.data);
      } catch (err) {
        console.error("Failed to load books", err);
      }
    };
    loadBooks();
  }, []);

  const filteredBooks = books.filter(
    (book) =>
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.author.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#FAFAFA", width: "100%" }}>
      {/* HEADER */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)",
          px: 4,
          py: 2,
          color: "white",
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
        }}
      >
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography variant="h6" fontWeight="700">
            LIBRARY HUB
          </Typography>
          <TextField
            placeholder="Search books..."
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{
              width: "35%",
              "& .MuiOutlinedInput-root": {
                bgcolor: "rgba(255,255,255,0.2)",
                borderRadius: "50px",
                color: "white",
                "& fieldset": { border: "none" },
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: "white", fontSize: 20 }} />
                </InputAdornment>
              ),
            }}
          />
          <Button
            onClick={logout}
            startIcon={<LogoutIcon />}
            sx={{ color: "white", textTransform: "none" }}
          >
            Logout
          </Button>
        </Box>
      </Box>

      {/* PLP SECTION */}
      <Box sx={{ p: 2 }}>
  <Grid container spacing={3}>
  {filteredBooks.map((book) => (
    /* Adjusted breakpoints: 1 per row on mobile, 2 on small, 3 on medium, 4 on large, 6 on extra-large */
    <Grid item xs={12} sm={6} md={4} lg={3} xl={2} key={book.id}>
      <Card
        sx={{
          height: 420, // Strict fixed height for every card in every row
          display: "flex",
          flexDirection: "column",
          borderRadius: "12px",
          border: "1px solid #E5E7EB",
          boxShadow: "none",
          transition: "transform 0.2s, box-shadow 0.2s",
          "&:hover": {
            borderColor: "#A78BFA",
            boxShadow: "0 10px 20px rgba(0,0,0,0.05)",
            transform: "translateY(-4px)"
          },
        }}
      >
        {/* 1. IMAGE SECTION: Strict height */}
        <Box sx={{ height: 180, minHeight: 180, position: "relative", overflow: "hidden" }}>
          <Box
            component="img"
            src={DEFAULT_BOOK_IMG}
            sx={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
          <IconButton
            sx={{ position: "absolute", top: 8, right: 8, bgcolor: "white", p: 0.5 }}
            size="small"
          >
            <BookmarkBorderIcon sx={{ color: "#EC4899", fontSize: "1.2rem" }} />
          </IconButton>
        </Box>

        <CardContent
          sx={{
            p: 2,
            flexGrow: 1, 
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* 2. ISBN SECTION: Fixed height container */}
          <Box sx={{ height: 20, overflow: "hidden" }}>
            <Typography variant="caption" color="text.disabled" fontWeight="700">
              ISBN: {book.isbn}
            </Typography>
          </Box>

          {/* 3. TITLE SECTION: Fixed height for exactly 2 lines */}
          <Box sx={{ height: 44, mt: 1, mb: 0.5, overflow: "hidden" }}>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 800,
                lineHeight: 1.2,
                fontSize: "0.95rem",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
              }}
            >
              {book.title}
            </Typography>
          </Box>

          {/* 4. AUTHOR SECTION: Fixed height for 1 line */}
          <Box sx={{ height: 22, mb: 2, overflow: "hidden" }}>
            <Typography variant="body2" color="text.secondary" noWrap>
              {book.author}
            </Typography>
          </Box>

          {/* 5. FOOTER SECTION: Forced to bottom with mt: 'auto' */}
          <Box sx={{ mt: "auto" }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
              <Chip
                label={book.available_copies > 0 ? "Available" : "Out of Stock"}
                size="small"
                sx={{
                  height: 22,
                  px: 0.5,
                  fontSize: "0.65rem",
                  fontWeight: 800,
                  bgcolor: book.available_copies > 0 ? "#DEF7EC" : "#FDE8E8",
                  color: book.available_copies > 0 ? "#03543F" : "#9B1C1C",
                  borderRadius: "6px"
                }}
              />
              <Typography variant="caption" fontWeight="800" color="text.primary">
                Qty: {book.available_copies}
              </Typography>
            </Box>

            <Button
              fullWidth
              variant="contained"
              disabled={book.available_copies === 0}
              sx={{
                background: "linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)",
                borderRadius: "8px",
                fontSize: "0.8rem",
                fontWeight: 700,
                textTransform: "none",
                py: 1,
                boxShadow: "0 4px 6px rgba(139, 92, 246, 0.2)",
                "&:hover": {
                   filter: "brightness(1.1)"
                }
              }}
            >
              Borrow
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  ))}
</Grid>
      </Box>
    </Box>
  );
}
