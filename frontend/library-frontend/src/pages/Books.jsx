import { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TablePagination,
  TableSortLabel
} from "@mui/material";

import { useAuth } from "../context/AuthContext";
import {
  getBooks,
  getCategories,
  addBook,
  updateBook,
  deleteBook,
  requestIssue
} from "../services/api";

import BookForm from "../components/BookForm";

function Books() {
  const { user } = useAuth();

  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);

  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("");

  const [open, setOpen] = useState(false);
  const [editingBook, setEditingBook] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // ================= PAGINATION =================
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [totalBooks, setTotalBooks] = useState(0);

  // ================= SORTING =================
  const [sortBy, setSortBy] = useState("title");
  const [order, setOrder] = useState("asc");

  // ================= FETCH BOOKS =================
  useEffect(() => {
    fetchBooks();
  }, [search, categoryId, page, rowsPerPage, sortBy, order]);

  const fetchBooks = async () => {
    try {
      const res = await getBooks(
        search,
        categoryId,
        page + 1,
        rowsPerPage,
        sortBy,
        order
      );

      setBooks(res.data.data);
      setTotalBooks(res.data.total);
      setError("");
    } catch (err) {
      handleError(err, "Failed to load books");
    }
  };

  // ================= FETCH CATEGORIES =================
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const res = await getCategories();
      setCategories(res.data);
    } catch (err) {
      handleError(err, "Failed to load categories");
    }
  };

  // ================= SORT HANDLER =================
  const handleSort = (column) => {
    const isAsc = sortBy === column && order === "asc";
    setSortBy(column);
    setOrder(isAsc ? "desc" : "asc");
  };

  // ================= SAVE =================
  const handleSave = async (data) => {
    try {
      setError("");
      setSuccess("");

      if (editingBook) {
        await updateBook(editingBook.id, data);
        setSuccess("Book updated successfully");
      } else {
        await addBook(data);
        setSuccess("Book added successfully");
      }

      setOpen(false);
      setEditingBook(null);
      fetchBooks();
    } catch (err) {
      handleError(err, "Failed to save book");
    }
  };

  // ================= DELETE =================
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this book?")) return;
    try {
      await deleteBook(id);
      setSuccess("Book deleted successfully");
      fetchBooks();
    } catch (err) {
      handleError(err, "Failed to delete book");
    }
  };

  // ================= ISSUE =================
  const handleRequestIssue = async (bookId) => {
    try {
      await requestIssue(bookId);
      setSuccess("Issue request sent to Admin");
      fetchBooks();
    } catch (err) {
      handleError(err, "Issue request failed");
    }
  };

  // ================= ERROR =================
  const handleError = (err, fallbackMessage) => {
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail;
      setError(Array.isArray(detail) ? detail.map(e => e.msg).join(", ") : detail);
    } else {
      setError(fallbackMessage);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Books
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      {/* SEARCH */}
      <TextField
        label="Search"
        fullWidth
        sx={{ mb: 2 }}
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(0);
        }}
      />

      {/* CATEGORY FILTER */}
      <TextField
        select
        label="Category"
        fullWidth
        sx={{ mb: 3 }}
        value={categoryId}
        onChange={(e) => {
          setCategoryId(e.target.value);
          setPage(0);
        }}
      >
        <MenuItem value="">All Categories</MenuItem>
        {categories.map((cat) => (
          <MenuItem key={cat.id} value={cat.id}>
            {cat.name}
          </MenuItem>
        ))}
      </TextField>

      {/* ADMIN ADD */}
      {user.role === "ADMIN" && (
        <Button variant="contained" sx={{ mb: 2 }} onClick={() => setOpen(true)}>
          Add Book
        </Button>
      )}

      {/* TABLE */}
      <Table>
        <TableHead>
          <TableRow>
            {[
              { id: "title", label: "Title" },
              { id: "author", label: "Author" },
              { id: "category_id", label: "Category" },
              { id: "available_copies", label: "Available" }
            ].map(col => (
              <TableCell key={col.id}>
                <TableSortLabel
                  active={sortBy === col.id}
                  direction={sortBy === col.id ? order : "asc"}
                  onClick={() => handleSort(col.id)}
                >
                  {col.label}
                </TableSortLabel>
              </TableCell>
            ))}
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {books.map(book => (
            <TableRow key={book.id}>
              <TableCell>{book.title}</TableCell>
              <TableCell>{book.author}</TableCell>
              <TableCell>{book.category?.name || "-"}</TableCell>
              <TableCell>{book.available_copies}</TableCell>

              <TableCell>
                {user.role === "ADMIN" ? (
                  <>
                    <Button onClick={() => {
                      setEditingBook(book);
                      setOpen(true);
                    }}>
                      Edit
                    </Button>
                    <Button color="error" onClick={() => handleDelete(book.id)}>
                      Delete
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="contained"
                    disabled={book.available_copies === 0}
                    onClick={() => handleRequestIssue(book.id)}
                  >
                    Request Issue
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* PAGINATION */}
      <TablePagination
        component="div"
        count={totalBooks}
        page={page}
        onPageChange={(_, newPage) => setPage(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
        rowsPerPageOptions={[5, 10, 20]}
      />

      {/* DIALOG */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingBook ? "Edit Book" : "Add Book"}</DialogTitle>
        <DialogContent>
          <BookForm
            book={editingBook}
            onSave={handleSave}
            categories={categories}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default Books;
