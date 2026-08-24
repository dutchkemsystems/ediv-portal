import { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, Button, Paper, Grid, Tabs, Tab, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Alert, Container, LinearProgress, TextField,
  MenuItem, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material'
import { Translate as TranslateIcon, Save as SaveIcon, Refresh as RefreshIcon, Edit as EditIcon } from '@mui/icons-material'
import api from '../api/client'

const lagosRed = '#C8102E'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'yo', label: 'Yoruba' },
  { code: 'pcm', label: 'Pidgin' },
  { code: 'fr', label: 'French' },
]

const SAMPLE_PREVIEW = {
  en: 'Welcome to Lagos Education District Portal',
  yo: 'Káàbọ̀ sí Etí Ijọba Alẹ́kọ̀ọ́ Ìpínlẹ̀ Èkó',
  pcm: 'Welcome for Lagos Education District Portal',
  fr: 'Bienvenue sur le portail du district éducatif de Lagos',
}

export default function Multilingual() {
  const [activeTab, setActiveTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Translations state
  const [translations, setTranslations] = useState([])
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [editForm, setEditForm] = useState({ english: '', yoruba: '', pidgin: '', french: '' })

  // Language settings state
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [currentLanguage, setCurrentLanguage] = useState('en')
  const [languageLoading, setLanguageLoading] = useState(false)

  const fetchTranslations = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/api/multilingual/translations/')
      setTranslations(res.data.results || res.data || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load translations.')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchMyLanguage = useCallback(async () => {
    setLanguageLoading(true)
    try {
      const res = await api.get('/api/multilingual/user-language-preferences/?user=current')
      const data = res.data.results || res.data || []
      if (Array.isArray(data) && data.length > 0) {
        setSelectedLanguage(data[0].language || 'en')
        setCurrentLanguage(data[0].language || 'en')
      }
    } catch (err) {
      // Ignore - user may not have a preference yet
    } finally {
      setLanguageLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTranslations()
    fetchMyLanguage()
  }, [fetchTranslations, fetchMyLanguage])

  const handleOpenEdit = (row) => {
    setEditingRow(row)
    setEditForm({
      english: row.english || row.en || '',
      yoruba: row.yoruba || row.yo || '',
      pidgin: row.pidgin || row.pcm || '',
      french: row.french || row.fr || '',
    })
    setEditDialogOpen(true)
  }

  const handleCloseEdit = () => {
    setEditDialogOpen(false)
    setEditingRow(null)
    setEditForm({ english: '', yoruba: '', pidgin: '', french: '' })
  }

  const handleSaveEdit = async () => {
    if (!editingRow) return
    setLoading(true)
    setError('')
    try {
      await api.put(`/api/multilingual/translations/${editingRow.id}/`, {
        key: editingRow.key,
        english: editForm.english,
        yoruba: editForm.yoruba,
        pidgin: editForm.pidgin,
        french: editForm.french,
      })
      setSuccess('Translation updated successfully.')
      handleCloseEdit()
      fetchTranslations()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update translation.')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveLanguage = async () => {
    setLanguageLoading(true)
    setError('')
    setSuccess('')
    try {
      await api.post('/api/multilingual/user-language-preferences/', {
        language: selectedLanguage,
      })
      setCurrentLanguage(selectedLanguage)
      setSuccess('Language preference saved successfully.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save language preference.')
    } finally {
      setLanguageLoading(false)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
          <TranslateIcon sx={{ fontSize: 32, color: lagosRed }} />
          <Typography variant="h4" sx={{ fontWeight: 700, color: lagosRed }}>
            Multilingual Support
          </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

        <Tabs
          value={activeTab}
          onChange={(_, v) => setActiveTab(v)}
          sx={{
            mb: 3,
            '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 },
            '& .MuiTabs-indicator': { backgroundColor: lagosRed },
          }}
        >
          <Tab label="Translations" />
          <Tab label="My Language Settings" />
        </Tabs>

        {activeTab === 0 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={fetchTranslations}
                disabled={loading}
                sx={{ borderColor: lagosRed, color: lagosRed, '&:hover': { borderColor: '#a00d24', bgcolor: 'rgba(200,16,46,0.04)' } }}
              >
                Refresh
              </Button>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2, '& .MuiLinearProgress-bar': { bgcolor: lagosRed }, bgcolor: '#fde8ec' }} />}

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                    <TableCell sx={{ fontWeight: 700 }}>Key</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>English</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Yoruba</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Pidgin</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>French</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {translations.length === 0 && !loading && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                          No translations found.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                  {translations.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{row.key}</TableCell>
                      <TableCell>{row.english || row.en || '—'}</TableCell>
                      <TableCell>{row.yoruba || row.yo || '—'}</TableCell>
                      <TableCell>{row.pidgin || row.pcm || '—'}</TableCell>
                      <TableCell>{row.french || row.fr || '—'}</TableCell>
                      <TableCell align="center">
                        <Button
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => handleOpenEdit(row)}
                          sx={{
                            color: lagosRed,
                            textTransform: 'none',
                            '&:hover': { bgcolor: 'rgba(200,16,46,0.04)' },
                          }}
                        >
                          Edit
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            {languageLoading && <LinearProgress sx={{ mb: 2, '& .MuiLinearProgress-bar': { bgcolor: lagosRed }, bgcolor: '#fde8ec' }} />}

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Preferred Language
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Select your preferred language for the portal interface.
                  </Typography>

                  <TextField
                    select
                    fullWidth
                    label="Language"
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    sx={{ mb: 2 }}
                  >
                    {LANGUAGES.map((lang) => (
                      <MenuItem key={lang.code} value={lang.code}>
                        {lang.label}
                      </MenuItem>
                    ))}
                  </TextField>

                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveLanguage}
                    disabled={languageLoading || selectedLanguage === currentLanguage}
                    sx={{
                      bgcolor: lagosRed,
                      textTransform: 'none',
                      fontWeight: 600,
                      '&:hover': { bgcolor: '#a00d24' },
                      '&.Mui-disabled': { bgcolor: '#ccc' },
                    }}
                  >
                    Save Preference
                  </Button>

                  {currentLanguage && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      Current language: <strong>{LANGUAGES.find((l) => l.code === currentLanguage)?.label || currentLanguage}</strong>
                    </Typography>
                  )}
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 3, bgcolor: '#fafafa' }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Language Preview
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    This is how a sample message will appear in your selected language.
                  </Typography>

                  <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fff', borderLeft: `4px solid ${lagosRed}` }}>
                    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      {LANGUAGES.find((l) => l.code === selectedLanguage)?.label || selectedLanguage}
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 0.5, fontWeight: 500 }}>
                      {SAMPLE_PREVIEW[selectedLanguage] || 'Preview not available.'}
                    </Typography>
                  </Paper>

                  <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {LANGUAGES.map((lang) => (
                      <Paper
                        key={lang.code}
                        variant="outlined"
                        sx={{
                          px: 1.5,
                          py: 0.5,
                          cursor: 'pointer',
                          borderColor: selectedLanguage === lang.code ? lagosRed : 'divider',
                          bgcolor: selectedLanguage === lang.code ? 'rgba(200,16,46,0.06)' : 'transparent',
                          '&:hover': { borderColor: lagosRed },
                          transition: 'all 0.15s',
                        }}
                        onClick={() => setSelectedLanguage(lang.code)}
                      >
                        <Typography variant="caption" sx={{ fontWeight: selectedLanguage === lang.code ? 700 : 400 }}>
                          {lang.label}
                        </Typography>
                      </Paper>
                    ))}
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Edit Translation Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={handleCloseEdit}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ fontWeight: 600 }}>
          Edit Translation — <Box component="span" sx={{ fontFamily: 'monospace', color: lagosRed }}>{editingRow?.key}</Box>
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="English"
                value={editForm.english}
                onChange={(e) => setEditForm((prev) => ({ ...prev, english: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Yoruba"
                value={editForm.yoruba}
                onChange={(e) => setEditForm((prev) => ({ ...prev, yoruba: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Pidgin"
                value={editForm.pidgin}
                onChange={(e) => setEditForm((prev) => ({ ...prev, pidgin: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="French"
                value={editForm.french}
                onChange={(e) => setEditForm((prev) => ({ ...prev, french: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button
            onClick={handleCloseEdit}
            sx={{ textTransform: 'none', color: 'text.secondary' }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveEdit}
            disabled={loading}
            sx={{
              bgcolor: lagosRed,
              textTransform: 'none',
              fontWeight: 600,
              '&:hover': { bgcolor: '#a00d24' },
            }}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
