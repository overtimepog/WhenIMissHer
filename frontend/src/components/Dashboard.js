import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { addEntry, getEntries, deleteEntry, updateEntry } from '../services/api';
import { format } from 'date-fns';

function Dashboard() {
  const [entries, setEntries] = useState([]);
  const [newEntry, setNewEntry] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [editDialog, setEditDialog] = useState({ open: false, entry: null });
  const [editContent, setEditContent] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      const data = await getEntries();
      setEntries(data);
    } catch (err) {
      setError('Failed to fetch entries');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await addEntry(newEntry);
      setNewEntry('');
      await fetchEntries();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteEntry(id);
      await fetchEntries();
    } catch (err) {
      setError('Failed to delete entry');
    }
  };

  const handleEdit = (entry) => {
    setEditDialog({ open: true, entry });
    setEditContent(entry.content);
  };

  const handleEditSubmit = async () => {
    try {
      await updateEntry(editDialog.entry.id, editContent);
      setEditDialog({ open: false, entry: null });
      await fetchEntries();
    } catch (err) {
      setError('Failed to update entry');
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Thoughts
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={newEntry}
              onChange={(e) => setNewEntry(e.target.value)}
              label="Write your thoughts..."
              variant="outlined"
              margin="normal"
            />

            {error && (
              <Alert severity="error" sx={{ my: 2 }}>
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              disabled={loading || !newEntry.trim()}
              sx={{ mt: 2 }}
            >
              {loading ? 'Saving...' : 'Save'}
            </Button>
          </form>
        </Paper>

        <List>
          {entries.map((entry) => (
            <Paper key={entry.id} elevation={2} sx={{ mb: 2 }}>
              <ListItem
                secondaryAction={
                  <Box>
                    <IconButton
                      edge="end"
                      aria-label="edit"
                      onClick={() => handleEdit(entry)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDelete(entry.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                }
              >
                <ListItemText
                  primary={entry.content}
                  secondary={format(new Date(entry.created_at), 'PPpp')}
                />
              </ListItem>
            </Paper>
          ))}
        </List>

        <Dialog open={editDialog.open} onClose={() => setEditDialog({ open: false, entry: null })}>
          <DialogTitle>Edit Entry</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              variant="outlined"
              margin="normal"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialog({ open: false, entry: null })}>
              Cancel
            </Button>
            <Button onClick={handleEditSubmit} variant="contained" color="primary">
              Save
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

export default Dashboard; 