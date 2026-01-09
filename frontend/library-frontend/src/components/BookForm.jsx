import { useState, useEffect } from 'react';
import { TextField, Button, Box, MenuItem } from '@mui/material';

function BookForm({ book, onSave, categories }) {
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    total_copies: 1,
    category_id: '',
  });

  useEffect(() => {
    if (book) {
      setFormData({
        title: book.title || '',
        author: book.author || '',
        isbn: book.isbn || '',
        total_copies: book.total_copies || 1,
        category_id: book.category?.id || '',
      });
    } else {
      setFormData({
        title: '',
        author: '',
        isbn: '',
        total_copies: 1,
        category_id: '',
      });
    }
  }, [book]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ 
      ...formData, 
      [name]: name === 'total_copies' ? Number(value) : value 
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title || !formData.author || !formData.isbn || !formData.total_copies || !formData.category_id) {
      alert('Please fill all fields correctly.');
      return;
    }
    onSave(formData);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField
        label="Title"
        name="title"
        value={formData.title}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      <TextField
        label="Author"
        name="author"
        value={formData.author}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      <TextField
        label="ISBN"
        name="isbn"
        value={formData.isbn}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
        disabled={!!book}
      />
      <TextField
        label="Total Copies"
        name="total_copies"
        type="number"
        value={formData.total_copies}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
        inputProps={{ min: 1 }}
      />
      <TextField
        select
        label="Category"
        name="category_id"
        value={formData.category_id}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      >
        <MenuItem value="">Select Category</MenuItem>
        {categories.map((cat) => (
          <MenuItem key={cat.id} value={cat.id}>
            {cat.name}
          </MenuItem>
        ))}
      </TextField>
      <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
        {book ? 'Update Book' : 'Add Book'}
      </Button>
    </Box>
  );
}

export default BookForm;
