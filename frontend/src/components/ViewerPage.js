import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
} from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';
import { getEntries, changePin } from '../services/api';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';

function ViewerPage() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [changePinDialog, setChangePinDialog] = useState(false);
  const [currentPin, setCurrentPin] = useState('');
  const [newPin, setNewPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [pinError, setPinError] = useState('');
  const [pinSuccess, setPinSuccess] = useState(false);
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
    } finally {
      setLoading(false);
    }
  };

  const handleChangePinClick = () => {
    setChangePinDialog(true);
    setPinError('');
    setPinSuccess(false);
    setCurrentPin('');
    setNewPin('');
    setConfirmPin('');
  };

  const handleChangePinClose = () => {
    setChangePinDialog(false);
  };

  const handleChangePinSubmit = async () => {
    try {
      setPinError('');

      if (newPin !== confirmPin) {
        setPinError('New PINs do not match');
        return;
      }

      if (!/^\d{4}$/.test(newPin)) {
        setPinError('PIN must be exactly 4 digits');
        return;
      }

      await changePin(currentPin, newPin);
      setPinSuccess(true);
      setTimeout(() => {
        setChangePinDialog(false);
        navigate('/');
      }, 2000);
    } catch (err) {
      setPinError(err.message);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Times They Thought About You
          </Typography>
          <IconButton
            onClick={handleChangePinClick}
            color="primary"
            size="large"
            title="Change PIN"
          >
            <SettingsIcon />
          </IconButton>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <List>
          {entries.map((entry) => (
            <Paper key={entry.id} elevation={2} sx={{ mb: 2 }}>
              <ListItem>
                <ListItemText
                  primary={
                    <Typography
                      component="div"
                      variant="body1"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        mb: 1,
                        fontStyle: 'italic',
                        color: 'text.primary',
                      }}
                    >
                      "{entry.content}"
                    </Typography>
                  }
                  secondary={
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ textAlign: 'right' }}
                    >
                      {format(new Date(entry.created_at), 'PPpp')}
                    </Typography>
                  }
                />
              </ListItem>
            </Paper>
          ))}
        </List>

        {entries.length === 0 && !error && (
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No entries yet. They will appear here when they think of you.
            </Typography>
          </Paper>
        )}

        <Dialog open={changePinDialog} onClose={handleChangePinClose}>
          <DialogTitle>Change Your PIN</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 1 }}>
              {pinSuccess ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  PIN changed successfully! Redirecting...
                </Alert>
              ) : (
                <>
                  {pinError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {pinError}
                    </Alert>
                  )}
                  <TextField
                    fullWidth
                    type="password"
                    label="Current PIN"
                    value={currentPin}
                    onChange={(e) => setCurrentPin(e.target.value)}
                    margin="normal"
                    inputProps={{ maxLength: 4, pattern: '[0-9]*' }}
                  />
                  <TextField
                    fullWidth
                    type="password"
                    label="New PIN"
                    value={newPin}
                    onChange={(e) => setNewPin(e.target.value)}
                    margin="normal"
                    inputProps={{ maxLength: 4, pattern: '[0-9]*' }}
                  />
                  <TextField
                    fullWidth
                    type="password"
                    label="Confirm New PIN"
                    value={confirmPin}
                    onChange={(e) => setConfirmPin(e.target.value)}
                    margin="normal"
                    inputProps={{ maxLength: 4, pattern: '[0-9]*' }}
                  />
                </>
              )}
            </Box>
          </DialogContent>
          {!pinSuccess && (
            <DialogActions>
              <Button onClick={handleChangePinClose}>Cancel</Button>
              <Button
                onClick={handleChangePinSubmit}
                variant="contained"
                disabled={!currentPin || !newPin || !confirmPin}
              >
                Change PIN
              </Button>
            </DialogActions>
          )}
        </Dialog>
      </Box>
    </Container>
  );
}

export default ViewerPage; 