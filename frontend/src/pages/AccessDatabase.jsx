import { useState, useEffect, useCallback, useRef } from 'react'
import { useSelector } from 'react-redux'
import {
  Box, Typography, Button, Grid, Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, FormControl, InputLabel, Select, MenuItem, Tabs,
  Tab, Paper, IconButton, Tooltip, Snackbar, Divider, LinearProgress,
  List, ListItemButton, ListItemText, ListItemIcon,
  InputAdornment, Alert, TablePagination,
} from '@mui/material'
import {
  Storage as DatabaseIcon, TableChart as TableIcon, Upload as UploadIcon,
  Delete as DeleteIcon, Add as AddIcon, Refresh as RefreshIcon,
  Download as DownloadIcon, Search as SearchIcon,
  ArrowUpward as ArrowUpIcon, ArrowDownward as ArrowDownIcon,
  CloudSync as SyncIcon, Security as SecurityIcon, Close as CloseIcon,
  MergeType as MergeIcon, Undo as UndoIcon, FindReplace as FindReplaceIcon,
  VerticalAlignBottom as FillDownIcon, FileDownload as ExportIcon,
  PersonAdd as PersonAddIcon, PersonRemove as PersonRemoveIcon,
  Storage as StorageIcon, ContentCopy as CopyIcon, CheckCircle as CheckIcon,
} from '@mui/icons-material'
import { DataGrid } from '@mui/x-data-grid'
import api from '../api/client'

const PRIMARY = '#C8102E'
const PRIMARY_DARK = '#9B0A22'
const LAGOS_LIGHT = '#FFF0F2'

const PRIVILEGE_LEVELS = [
  { value: 'VIEW', label: 'View Only', color: 'info' },
  { value: 'EDIT', label: 'Edit', color: 'primary' },
  { value: 'DELETE', label: 'Delete', color: 'warning' },
  { value: 'ADMIN', label: 'Full Admin', color: 'error' },
]

const SYNC_TARGETS = [
  { value: 'students', label: 'Students' },
  { value: 'staff', label: 'Staff' },
  { value: 'schools', label: 'Schools' },
]

function AccessDatabase() {
  const { user } = useSelector((state) => state.auth)
  const canManage = user?.role === 'SYSADMIN' || user?.role === 'TG_PS'

  const [mainTab, setMainTab] = useState(0)
  const [databases, setDatabases] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedDb, setSelectedDb] = useState(null)
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState('')
  const [tableData, setTableData] = useState({ rows: [], columns: [], total: 0 })
  const [dataLoading, setDataLoading] = useState(false)
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(50)
  const [sortModel, setSortModel] = useState([])
  const [filterText, setFilterText] = useState('')
  const [selectedRows, setSelectedRows] = useState([])
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadDbName, setUploadDbName] = useState('')
  const [uploadDesc, setUploadDesc] = useState('')
  const [uploading, setUploading] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [dbToDelete, setDbToDelete] = useState(null)
  const [accessUsers, setAccessUsers] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [grantUserId, setGrantUserId] = useState('')
  const [grantLevel, setGrantLevel] = useState('VIEW')
  const [syncDialogOpen, setSyncDialogOpen] = useState(false)
  const [syncTarget, setSyncTarget] = useState('')
  const [editingCell, setEditingCell] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [findReplaceOpen, setFindReplaceOpen] = useState(false)
  const [findValue, setFindValue] = useState('')
  const [replaceValue, setReplaceValue] = useState('')
  const [findColumn, setFindColumn] = useState('')
  const [fillDownOpen, setFillDownOpen] = useState(false)
  const [fillDownColumn, setFillDownColumn] = useState('')
  const [copyColumnOpen, setCopyColumnOpen] = useState(false)
  const [copySourceCol, setCopySourceCol] = useState('')
  const [copyTargetCol, setCopyTargetCol] = useState('')
  const [mergeDialogOpen, setMergeDialogOpen] = useState(false)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })
  const fileInputRef = useRef(null)

  const showSnackbar = useCallback((message, severity = 'success') => {
    setSnackbar({ open: true, message, severity })
  }, [])

  const fetchDatabases = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/access-databases/')
      setDatabases(res.data.results || res.data || [])
    } catch {
      showSnackbar('Failed to load databases', 'error')
    } finally {
      setLoading(false)
    }
  }, [showSnackbar])

  const fetchTables = useCallback(async (dbId) => {
    if (!dbId) return
    try {
      const res = await api.get(`/access-databases/${dbId}/tables/`)
      setTables(res.data.results || res.data || [])
    } catch {
      showSnackbar('Failed to load tables', 'error')
    }
  }, [showSnackbar])

  const fetchTableData = useCallback(async (dbId, tableName, pg, pgSize, sort, filter) => {
    if (!dbId || !tableName) return
    setDataLoading(true)
    try {
      const params = new URLSearchParams({ table_name: tableName, page: pg + 1, page_size: pgSize })
      if (sort && sort.length > 0) {
        params.append('sort_by', sort[0].field)
        params.append('sort_order', sort[0].sort)
      }
      if (filter) params.append('filter', filter)
      const res = await api.get(`/access-databases/${dbId}/table-data/?${params.toString()}`)
      const data = res.data
      const rows = (data.results || data.rows || []).map((row, idx) => ({
        ...row,
        _rowId: row.id || row.pk || `${pg * pgSize + idx}`,
      }))
      const cols = data.columns || Object.keys(rows[0] || {}).filter(k => !k.startsWith('_'))
      setTableData({ rows, columns: cols, total: data.count || data.total || rows.length })
    } catch {
      showSnackbar('Failed to load table data', 'error')
    } finally {
      setDataLoading(false)
    }
  }, [showSnackbar])

  const fetchAccessUsers = useCallback(async (dbId) => {
    if (!dbId) return
    try {
      const res = await api.get(`/access-databases/${dbId}/`)
      setAccessUsers(res.data.access_users || res.data.access_list || [])
    } catch { setAccessUsers([]) }
  }, [])

  const fetchAllUsers = useCallback(async () => {
    try {
      const res = await api.get('/users/school-staff/')
      setAllUsers(res.data.results || res.data || [])
    } catch { setAllUsers([]) }
  }, [])

  useEffect(() => { fetchDatabases() }, [fetchDatabases])

  useEffect(() => {
    if (mainTab === 3 && selectedDb) {
      fetchAccessUsers(selectedDb.id)
      fetchAllUsers()
    }
  }, [mainTab, selectedDb, fetchAccessUsers, fetchAllUsers])

  useEffect(() => {
    if (selectedDb && selectedTable) {
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    }
  }, [selectedDb, selectedTable, page, pageSize, sortModel, filterText, fetchTableData])

  const handleOpenDatabase = (db) => {
    setSelectedDb(db)
    setSelectedTable('')
    setTableData({ rows: [], columns: [], total: 0 })
    setPage(0)
    setSelectedRows([])
    setSortModel([])
    setFilterText('')
    setMainTab(1)
    fetchTables(db.id)
  }

  const handleSelectTable = (tableName) => {
    setSelectedTable(tableName)
    setPage(0)
    setSelectedRows([])
    setSortModel([])
  }

  const handleUpload = async () => {
    if (!uploadFile) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', uploadFile)
      if (uploadDbName) formData.append('name', uploadDbName)
      if (uploadDesc) formData.append('description', uploadDesc)
      await api.post('/access-databases/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      showSnackbar('Database uploaded successfully')
      setUploadDialogOpen(false)
      setUploadFile(null)
      setUploadDbName('')
      setUploadDesc('')
      fetchDatabases()
    } catch (error) {
      showSnackbar(error.response?.data?.detail || error.response?.data?.error || 'Upload failed', 'error')
    } finally { setUploading(false) }
  }

  const handleDelete = async () => {
    if (!dbToDelete) return
    try {
      await api.delete(`/access-databases/${dbToDelete.id}/`)
      showSnackbar('Database deleted successfully')
      setDeleteDialogOpen(false)
      setDbToDelete(null)
      if (selectedDb?.id === dbToDelete.id) {
        setSelectedDb(null)
        setSelectedTable('')
        setTableData({ rows: [], columns: [], total: 0 })
        setMainTab(0)
      }
      fetchDatabases()
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Delete failed', 'error')
    }
  }

  const handleCellSave = async (rowId, field) => {
    if (!selectedDb || !selectedTable) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/update-cell/`, {
        table_name: selectedTable, row_id: rowId, column: field, value: editValue,
      })
      setTableData((prev) => ({
        ...prev,
        rows: prev.rows.map((r) => r._rowId === rowId ? { ...r, [field]: editValue } : r),
      }))
      showSnackbar('Cell updated')
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Update failed', 'error')
    } finally { setEditingCell(null) }
  }

  const handleDeleteRow = async (rowId) => {
    if (!selectedDb || !selectedTable) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/delete-row/`, { table_name: selectedTable, row_id: rowId })
      showSnackbar('Row deleted')
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Delete failed', 'error')
    }
  }

  const handleBulkDelete = async () => {
    if (!selectedDb || !selectedTable || selectedRows.length === 0) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/delete-rows/`, { table_name: selectedTable, row_ids: selectedRows })
      showSnackbar(`${selectedRows.length} rows deleted`)
      setSelectedRows([])
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Bulk delete failed', 'error')
    }
  }

  const handleRevertRow = async (rowId) => {
    if (!selectedDb || !selectedTable) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/revert-row/`, { table_name: selectedTable, row_id: rowId })
      showSnackbar('Row reverted to original')
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Revert failed', 'error')
    }
  }

  const handleMergeRows = async () => {
    if (!selectedDb || !selectedTable || selectedRows.length < 2) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/merge-rows/`, { table_name: selectedTable, row_ids: selectedRows })
      showSnackbar('Rows merged successfully')
      setSelectedRows([])
      setMergeDialogOpen(false)
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Merge failed', 'error')
    }
  }

  const handleGrantAccess = async () => {
    if (!selectedDb || !grantUserId) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/grant-access/`, { user_id: grantUserId, privilege_level: grantLevel })
      showSnackbar('Access granted successfully')
      setGrantUserId('')
      setGrantLevel('VIEW')
      fetchAccessUsers(selectedDb.id)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Grant failed', 'error')
    }
  }

  const handleRevokeAccess = async (userId) => {
    if (!selectedDb) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/revoke-access/`, { user_id: userId })
      showSnackbar('Access revoked')
      fetchAccessUsers(selectedDb.id)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Revoke failed', 'error')
    }
  }

  const handleSync = async () => {
    if (!selectedDb || !syncTarget) return
    try {
      await api.post(`/access-databases/${selectedDb.id}/sync-to-portal/`, { target_model: syncTarget })
      showSnackbar(`Data synced to ${syncTarget} successfully`)
      setSyncDialogOpen(false)
      setSyncTarget('')
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Sync failed', 'error')
    }
  }

  const handleExport = async (format = 'csv') => {
    if (!selectedDb || !selectedTable) return
    try {
      const res = await api.get(`/access-databases/${selectedDb.id}/export/?table_name=${selectedTable}&format=${format}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${selectedTable}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      showSnackbar(`Exported as ${format.toUpperCase()}`)
    } catch (error) {
      showSnackbar('Export failed', 'error')
    }
  }

  const handleExportSelected = async () => {
    if (!selectedDb || !selectedTable || selectedRows.length === 0) return
    try {
      const res = await api.post(`/access-databases/${selectedDb.id}/spreadsheet-ops/`,
        { table_name: selectedTable, operation: 'export_selected', row_ids: selectedRows, format: 'csv' },
        { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${selectedTable}_selected.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      showSnackbar('Selected rows exported')
    } catch (error) {
      showSnackbar('Export failed', 'error')
    }
  }

  const handleFindReplace = async () => {
    if (!selectedDb || !selectedTable || !findValue) return
    try {
      const res = await api.post(`/access-databases/${selectedDb.id}/spreadsheet-ops/`, {
        table_name: selectedTable, operation: 'find_replace', find: findValue, replace: replaceValue, column: findColumn || undefined,
      })
      showSnackbar(res.data.message || `Replaced ${res.data.count || 0} occurrences`)
      setFindReplaceOpen(false)
      setFindValue('')
      setReplaceValue('')
      setFindColumn('')
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Find & Replace failed', 'error')
    }
  }

  const handleFillDown = async () => {
    if (!selectedDb || !selectedTable || !fillDownColumn) return
    try {
      const res = await api.post(`/access-databases/${selectedDb.id}/spreadsheet-ops/`, {
        table_name: selectedTable, operation: 'fill_down', column: fillDownColumn,
      })
      showSnackbar(res.data.message || 'Fill down completed')
      setFillDownOpen(false)
      setFillDownColumn('')
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Fill down failed', 'error')
    }
  }

  const handleCopyColumn = async () => {
    if (!selectedDb || !selectedTable || !copySourceCol || !copyTargetCol) return
    try {
      const res = await api.post(`/access-databases/${selectedDb.id}/spreadsheet-ops/`, {
        table_name: selectedTable, operation: 'copy_column', source_column: copySourceCol, target_column: copyTargetCol,
      })
      showSnackbar(res.data.message || 'Column copied')
      setCopyColumnOpen(false)
      setCopySourceCol('')
      setCopyTargetCol('')
      fetchTableData(selectedDb.id, selectedTable, page, pageSize, sortModel, filterText)
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Copy column failed', 'error')
    }
  }

  const gridColumns = [
    ...tableData.columns.map((col) => ({
      field: col,
      headerName: col,
      flex: 1,
      minWidth: 130,
      editable: canManage && mainTab === 1,
      renderCell: (params) => {
        if (editingCell?.id === params.id && editingCell?.field === params.field) {
          return (
            <TextField size="small" fullWidth value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={() => handleCellSave(params.id, params.field)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCellSave(params.id, params.field)
                if (e.key === 'Escape') setEditingCell(null)
              }}
              autoFocus variant="outlined"
              sx={{ '& .MuiInputBase-input': { py: '4px', fontSize: 13 } }} />
          )
        }
        return (
          <Box sx={{ width: '100%', cursor: canManage ? 'pointer' : 'default', py: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
            onDoubleClick={() => {
              if (!canManage) return
              setEditingCell({ id: params.id, field: params.field })
              setEditValue(params.value ?? '')
            }}>
            {params.value != null ? String(params.value) : ''}
          </Box>
        )
      },
    })),
    ...(canManage && selectedTable && mainTab === 1 ? [{
      field: '_actions', headerName: 'Actions', width: 120, sortable: false, filterable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="Revert">
            <IconButton size="small" color="warning" onClick={() => handleRevertRow(params.row._rowId)}><UndoIcon fontSize="small" /></IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error" onClick={() => handleDeleteRow(params.row._rowId)}><DeleteIcon fontSize="small" /></IconButton>
          </Tooltip>
        </Box>
      ),
    }] : []),
  ]

  const renderDatabaseList = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight="bold" sx={{ color: PRIMARY_DARK }}>Microsoft Access Databases</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>Manage uploaded .accdb and .mdb files</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchDatabases}
            sx={{ borderColor: PRIMARY, color: PRIMARY, '&:hover': { borderColor: PRIMARY_DARK, bgcolor: LAGOS_LIGHT } }}>Refresh</Button>
          {canManage && (
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setUploadDialogOpen(true)}
              sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Upload Database</Button>
          )}
        </Box>
      </Box>
      {loading ? (<LinearProgress sx={{ borderRadius: 2 }} />)
      : databases.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <StorageIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">No databases uploaded</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Upload an Access database to get started</Typography>
          {canManage && (
            <Button variant="contained" startIcon={<UploadIcon />} onClick={() => setUploadDialogOpen(true)}
              sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Upload Database</Button>
          )}
        </Paper>
      ) : (
        <Grid container spacing={2}>
          {databases.map((db) => (
            <Grid item xs={12} sm={6} md={4} key={db.id}>
              <Paper sx={{ p: 0, cursor: 'pointer', transition: 'all 0.2s', overflow: 'hidden', border: '1px solid', borderColor: 'divider',
                '&:hover': { borderColor: PRIMARY, boxShadow: '0 4px 20px rgba(200,16,46,0.12)', transform: 'translateY(-2px)' } }}
                onClick={() => handleOpenDatabase(db)}>
                <Box sx={{ bgcolor: PRIMARY, color: 'white', p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <DatabaseIcon sx={{ fontSize: 32 }} />
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="subtitle1" fontWeight="bold" noWrap>{db.name || db.filename}</Typography>
                    <Typography variant="caption" sx={{ opacity: 0.85 }}>
                      {db.file_size ? `${(db.file_size / 1024 / 1024).toFixed(1)} MB` : 'Unknown size'}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                    <Chip icon={<TableIcon sx={{ fontSize: 14 }} />} label={`${db.table_count || 0} tables`} size="small" variant="outlined" />
                    <Chip icon={<StorageIcon sx={{ fontSize: 14 }} />} label={`${db.record_count || 0} records`} size="small" variant="outlined" />
                    <Chip label={db.status || 'READY'} size="small"
                      color={db.status === 'READY' || !db.status ? 'success' : db.status === 'ERROR' ? 'error' : 'warning'} />
                  </Box>
                  {db.description && <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }} noWrap>{db.description}</Typography>}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5 }}>
                    <Typography variant="caption" color="text.secondary">{db.uploaded_at ? new Date(db.uploaded_at).toLocaleDateString() : ''}</Typography>
                    {canManage && (
                      <IconButton size="small" color="error" onClick={(e) => { e.stopPropagation(); setDbToDelete(db); setDeleteDialogOpen(true) }}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    )}
                  </Box>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )

  const renderDataBrowser = () => {
    if (!selectedDb) {
      return (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <DatabaseIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">Select a database to browse</Typography>
          <Typography variant="body2" color="text.secondary">Go to the Databases tab and click on a database</Typography>
        </Paper>
      )
    }

    const allColumns = [
      { field: '_rowId', headerName: '#', width: 60, sortable: false },
      ...gridColumns,
    ]

    return (
      <Box sx={{ display: 'flex', height: 'calc(100vh - 220px)', minHeight: 500 }}>
        <Paper sx={{ width: 260, flexShrink: 0, mr: 2, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: LAGOS_LIGHT }}>
            <Typography variant="subtitle2" fontWeight="bold" sx={{ color: PRIMARY_DARK }}>{selectedDb.name || selectedDb.filename}</Typography>
            <Typography variant="caption" color="text.secondary">{tables.length} table{tables.length !== 1 ? 's' : ''}</Typography>
          </Box>
          <List sx={{ flex: 1, overflow: 'auto', py: 0 }}>
            {tables.map((table) => {
              const tableName = typeof table === 'string' ? table : table.name || table.table_name
              const rowCount = typeof table === 'object' ? table.row_count || table.record_count : null
              return (
                <ListItemButton key={tableName} selected={selectedTable === tableName}
                  onClick={() => handleSelectTable(tableName)} sx={{ py: 1 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <TableIcon fontSize="small" sx={{ color: selectedTable === tableName ? PRIMARY : 'text.secondary' }} />
                  </ListItemIcon>
                  <ListItemText primary={tableName} secondary={rowCount != null ? `${rowCount} rows` : null}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: selectedTable === tableName ? 'bold' : 'normal' }}
                    secondaryTypographyProps={{ variant: 'caption' }} />
                </ListItemButton>
              )
            })}
            {tables.length === 0 && (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">No tables found</Typography>
              </Box>
            )}
          </List>
        </Paper>

        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          {selectedTable && (
            <Paper sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, py: 1, flexWrap: 'wrap' }}>
                <Typography variant="subtitle2" fontWeight="bold" sx={{ mr: 1, color: PRIMARY_DARK }}>{selectedTable}</Typography>
                <Divider orientation="vertical" flexItem />
                <TextField size="small" placeholder="Filter rows..." value={filterText}
                  onChange={(e) => { setFilterText(e.target.value); setPage(0) }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
                    endAdornment: filterText && (
                      <InputAdornment position="end">
                        <IconButton size="small" onClick={() => { setFilterText(''); setPage(0) }}><CloseIcon fontSize="small" /></IconButton>
                      </InputAdornment>
                    ),
                  }} sx={{ width: 200 }} />
                <Divider orientation="vertical" flexItem />
                <Tooltip title="Sort Ascending">
                  <IconButton size="small" onClick={() => { if (tableData.columns.length > 0) setSortModel([{ field: tableData.columns[0], sort: 'asc' }]) }}>
                    <ArrowUpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Sort Descending">
                  <IconButton size="small" onClick={() => { if (tableData.columns.length > 0) setSortModel([{ field: tableData.columns[0], sort: 'desc' }]) }}>
                    <ArrowDownIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Divider orientation="vertical" flexItem />
                {canManage && (
                  <>
                    <Tooltip title="Find & Replace"><IconButton size="small" onClick={() => setFindReplaceOpen(true)}><FindReplaceIcon fontSize="small" /></IconButton></Tooltip>
                    <Tooltip title="Fill Down"><IconButton size="small" onClick={() => setFillDownOpen(true)}><FillDownIcon fontSize="small" /></IconButton></Tooltip>
                    <Tooltip title="Copy Column"><IconButton size="small" onClick={() => setCopyColumnOpen(true)}><CopyIcon fontSize="small" /></IconButton></Tooltip>
                  </>
                )}
                <Divider orientation="vertical" flexItem />
                <Tooltip title="Export CSV"><IconButton size="small" onClick={() => handleExport('csv')}><ExportIcon fontSize="small" /></IconButton></Tooltip>
                <Tooltip title="Export JSON"><IconButton size="small" onClick={() => handleExport('json')}><DownloadIcon fontSize="small" /></IconButton></Tooltip>
                {canManage && (
                  <Tooltip title="Sync to Portal"><IconButton size="small" color="primary" onClick={() => setSyncDialogOpen(true)}><SyncIcon fontSize="small" /></IconButton></Tooltip>
                )}
              </Box>
              {selectedRows.length > 0 && canManage && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, py: 1, bgcolor: LAGOS_LIGHT, borderTop: 1, borderColor: 'divider' }}>
                  <Chip label={`${selectedRows.length} selected`} size="small" color="primary" />
                  <Button size="small" color="error" startIcon={<DeleteIcon />} onClick={handleBulkDelete}>Delete Selected</Button>
                  <Button size="small" color="warning" startIcon={<MergeIcon />} onClick={() => setMergeDialogOpen(true)} disabled={selectedRows.length < 2}>Merge Selected</Button>
                  <Button size="small" startIcon={<ExportIcon />} onClick={handleExportSelected}>Export Selected</Button>
                </Box>
              )}
            </Paper>
          )}

          <Paper sx={{ flex: 1, display: 'flex' }}>
            {dataLoading ? (
              <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <LinearProgress sx={{ width: '60%' }} />
              </Box>
            ) : selectedTable ? (
              <DataGrid
                rows={tableData.rows}
                columns={allColumns}
                rowCount={tableData.total}
                loading={dataLoading}
                paginationMode="server"
                pagination
                page={page}
                pageSize={pageSize}
                onPageChange={(newPage) => setPage(newPage)}
                onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(0) }}
                rowsPerPageOptions={[10, 25, 50, 100]}
                sortingMode="server"
                sortModel={sortModel}
                onSortModelChange={(newSort) => { setSortModel(newSort); setPage(0) }}
                checkboxSelection={canManage}
                disableRowSelectionOnClick={false}
                onRowSelectionModelChange={(newSelection) => setSelectedRows(newSelection)}
                rowSelectionModel={selectedRows}
                onCellEditStart={(params) => {
                  if (!canManage) return
                  setEditingCell({ id: params.id, field: params.field })
                  setEditValue(params.value ?? '')
                }}
                processRowUpdate={(newRow) => newRow}
                getRowId={(row) => row._rowId}
                sx={{
                  border: 0,
                  '& .MuiDataGrid-columnHeaders': { bgcolor: LAGOS_LIGHT },
                  '& .MuiDataGrid-columnHeaderTitle': { fontWeight: 'bold' },
                  '& .MuiDataGrid-row:hover': { bgcolor: 'rgba(200,16,46,0.04)' },
                  '& .MuiDataGrid-cell': { borderBottom: '1px solid #f0f0f0' },
                  '& .MuiDataGrid-selected': { bgcolor: 'rgba(200,16,46,0.08)' },
                }}
              />
            ) : (
              <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">Select a table to view data</Typography>
              </Box>
            )}
          </Paper>
          {selectedTable && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
              <TablePagination component="div" count={tableData.total} page={page}
                onPageChange={(e, newPage) => setPage(newPage)} rowsPerPage={pageSize}
                onRowsPerPageChange={(e) => { setPageSize(parseInt(e.target.value)); setPage(0) }}
                rowsPerPageOptions={[10, 25, 50, 100]} />
            </Box>
          )}
        </Box>
      </Box>
    )
  }

  const renderPrivileges = () => {
    if (!selectedDb) {
      return (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <SecurityIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">Select a database first</Typography>
          <Typography variant="body2" color="text.secondary">Go to Databases tab and open a database to manage privileges</Typography>
        </Paper>
      )
    }
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h6" fontWeight="bold" sx={{ color: PRIMARY_DARK }}>Privilege Management</Typography>
            <Typography variant="body2" color="text.secondary">Manage user access for {selectedDb.name || selectedDb.filename}</Typography>
          </Box>
        </Box>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 2 }}>Grant Access</Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
            <FormControl sx={{ minWidth: 250 }}>
              <InputLabel>Select User</InputLabel>
              <Select value={grantUserId} onChange={(e) => setGrantUserId(e.target.value)} label="Select User">
                {allUsers.map((u) => (
                  <MenuItem key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.role || u.username})</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Privilege Level</InputLabel>
              <Select value={grantLevel} onChange={(e) => setGrantLevel(e.target.value)} label="Privilege Level">
                {PRIVILEGE_LEVELS.map((p) => (
                  <MenuItem key={p.value} value={p.value}>{p.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button variant="contained" startIcon={<PersonAddIcon />} onClick={handleGrantAccess} disabled={!grantUserId}
              sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Grant</Button>
          </Box>
        </Paper>
        <Paper>
          <Typography variant="subtitle2" fontWeight="bold" sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            Users with Access ({accessUsers.length})
          </Typography>
          {accessUsers.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">No users have been granted access yet</Typography>
            </Box>
          ) : (
            <List sx={{ py: 0 }}>
              {accessUsers.map((access, idx) => {
                const privilege = access.privilege_level || access.permission || 'VIEW'
                const levelInfo = PRIVILEGE_LEVELS.find((p) => p.value === privilege) || PRIVILEGE_LEVELS[0]
                return (
                  <Box key={access.id || idx}>
                    <ListItemButton sx={{ py: 1.5 }}>
                      <ListItemIcon sx={{ minWidth: 40 }}><SecurityIcon fontSize="small" sx={{ color: PRIMARY }} /></ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" fontWeight="medium">{access.username || access.user_name || `User ${access.user_id}`}</Typography>
                            <Chip label={levelInfo.label} size="small" color={levelInfo.color} variant="outlined" />
                          </Box>
                        }
                        secondary={access.email || access.granted_at ? `Granted ${new Date(access.granted_at).toLocaleDateString()}` : ''} />
                      <IconButton size="small" color="error" onClick={() => handleRevokeAccess(access.user_id)}>
                        <PersonRemoveIcon fontSize="small" />
                      </IconButton>
                    </ListItemButton>
                    {idx < accessUsers.length - 1 && <Divider />}
                  </Box>
                )
              })}
            </List>
          )}
        </Paper>
      </Box>
    )
  }

  const renderSync = () => {
    if (!selectedDb) {
      return (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <SyncIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">Select a database first</Typography>
          <Typography variant="body2" color="text.secondary">Go to Databases tab and open a database to sync</Typography>
        </Paper>
      )
    }
    return (
      <Box>
        <Typography variant="h6" fontWeight="bold" sx={{ color: PRIMARY_DARK, mb: 3 }}>Sync to Portal</Typography>
        <Paper sx={{ p: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Sync Access table data from <strong>{selectedDb.name || selectedDb.filename}</strong> to Django portal models. Select a target model below and confirm the sync operation.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            {SYNC_TARGETS.map((target) => (
              <Paper key={target.value} sx={{
                p: 3, flex: 1, cursor: 'pointer', transition: 'all 0.2s',
                border: '2px solid', borderColor: syncTarget === target.value ? PRIMARY : 'divider',
                '&:hover': { borderColor: PRIMARY },
              }} onClick={() => setSyncTarget(target.value)}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {syncTarget === target.value && <CheckIcon sx={{ color: PRIMARY }} />}
                  <Typography variant="subtitle1" fontWeight="bold">{target.label}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">Map Access tables to the {target.label.toLowerCase()} model</Typography>
              </Paper>
            ))}
          </Box>
          <Button variant="contained" startIcon={<SyncIcon />} onClick={() => setSyncDialogOpen(true)} disabled={!syncTarget}
            sx={{ mt: 3, bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Sync Data</Button>
        </Paper>
      </Box>
    )
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa' }}>
      <Box sx={{ bgcolor: 'white', borderBottom: 1, borderColor: 'divider', px: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box sx={{ bgcolor: PRIMARY, borderRadius: 1.5, p: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <DatabaseIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="h6" fontWeight="bold" sx={{ color: PRIMARY_DARK, lineHeight: 1.2 }}>Access Database Manager</Typography>
              <Typography variant="caption" color="text.secondary">Manage Microsoft Access databases and data</Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {selectedDb && (
              <Chip icon={<DatabaseIcon sx={{ fontSize: 14 }} />} label={selectedDb.name || selectedDb.filename}
                onDelete={() => { setSelectedDb(null); setSelectedTable(''); setMainTab(0) }}
                sx={{ '& .MuiChip-deleteIcon': { fontSize: 16 } }} />
            )}
          </Box>
        </Box>
        <Tabs value={mainTab} onChange={(_, v) => setMainTab(v)}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 500, minHeight: 44 } }}>
          <Tab label="Databases" />
          <Tab label="Data Browser" disabled={!selectedDb} />
          <Tab label="Privileges" disabled={!selectedDb} />
          <Tab label="Sync" disabled={!selectedDb} />
        </Tabs>
      </Box>
      <Box sx={{ p: 3 }}>
        {mainTab === 0 && renderDatabaseList()}
        {mainTab === 1 && renderDataBrowser()}
        {mainTab === 2 && renderPrivileges()}
        {mainTab === 3 && renderSync()}
      </Box>

      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <UploadIcon sx={{ color: PRIMARY }} /> Upload Access Database
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Button variant="outlined" fullWidth component="label" sx={{
              borderStyle: 'dashed', borderWidth: 2, py: 3, mb: 2,
              borderColor: uploadFile ? PRIMARY : 'text.secondary', bgcolor: uploadFile ? LAGOS_LIGHT : 'transparent',
            }}>
              <input ref={fileInputRef} type="file" hidden accept=".accdb,.mdb"
                onChange={(e) => setUploadFile(e.target.files[0])} />
              <Box sx={{ textAlign: 'center' }}>
                <UploadIcon sx={{ fontSize: 40, color: uploadFile ? PRIMARY : 'text.secondary', mb: 1 }} />
                <Typography variant="body1">{uploadFile ? uploadFile.name : 'Click to select .accdb or .mdb file'}</Typography>
                <Typography variant="caption" color="text.secondary">Supported formats: .accdb, .mdb</Typography>
              </Box>
            </Button>
            <TextField fullWidth label="Database Name" value={uploadDbName}
              onChange={(e) => setUploadDbName(e.target.value)} placeholder="Optional name for the database" sx={{ mb: 2 }} />
            <TextField fullWidth label="Description" value={uploadDesc} onChange={(e) => setUploadDesc(e.target.value)}
              multiline rows={2} placeholder="Optional description" />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => { setUploadDialogOpen(false); setUploadFile(null); setUploadDbName(''); setUploadDesc('') }}>Cancel</Button>
          <Button variant="contained" onClick={handleUpload} disabled={!uploadFile || uploading}
            startIcon={uploading ? <LinearProgress sx={{ width: 16 }} /> : <UploadIcon />}
            sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DeleteIcon sx={{ color: 'error.main' }} /> Delete Database
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            Are you sure you want to delete <strong>{dbToDelete?.name || dbToDelete?.filename}</strong>? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDelete} startIcon={<DeleteIcon />}>Delete</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={findReplaceOpen} onClose={() => setFindReplaceOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FindReplaceIcon sx={{ color: PRIMARY }} /> Find and Replace
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Column (optional - all columns if empty)</InputLabel>
              <Select value={findColumn} onChange={(e) => setFindColumn(e.target.value)} label="Column (optional - all columns if empty)">
                <MenuItem value="">All Columns</MenuItem>
                {tableData.columns.map((col) => (<MenuItem key={col} value={col}>{col}</MenuItem>))}
              </Select>
            </FormControl>
            <TextField fullWidth label="Find" value={findValue} onChange={(e) => setFindValue(e.target.value)} sx={{ mb: 2 }}
              InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }} />
            <TextField fullWidth label="Replace with" value={replaceValue} onChange={(e) => setReplaceValue(e.target.value)} />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFindReplaceOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleFindReplace} disabled={!findValue}
            sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Replace All</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={fillDownOpen} onClose={() => setFillDownOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FillDownIcon sx={{ color: PRIMARY }} /> Fill Down
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }} color="text.secondary">
            Fill empty cells with the value from the cell above in the selected column.
          </Typography>
          <FormControl fullWidth>
            <InputLabel>Select Column</InputLabel>
            <Select value={fillDownColumn} onChange={(e) => setFillDownColumn(e.target.value)} label="Select Column">
              {tableData.columns.map((col) => (<MenuItem key={col} value={col}>{col}</MenuItem>))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFillDownOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleFillDown} disabled={!fillDownColumn}
            sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Fill Down</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={copyColumnOpen} onClose={() => setCopyColumnOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CopyIcon sx={{ color: PRIMARY }} /> Copy Column
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }} color="text.secondary">
            Copy all values from one column to another.
          </Typography>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Source Column</InputLabel>
            <Select value={copySourceCol} onChange={(e) => setCopySourceCol(e.target.value)} label="Source Column">
              {tableData.columns.map((col) => (<MenuItem key={col} value={col}>{col}</MenuItem>))}
            </Select>
          </FormControl>
          <FormControl fullWidth>
            <InputLabel>Target Column</InputLabel>
            <Select value={copyTargetCol} onChange={(e) => setCopyTargetCol(e.target.value)} label="Target Column">
              {tableData.columns.map((col) => (<MenuItem key={col} value={col}>{col}</MenuItem>))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCopyColumnOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCopyColumn} disabled={!copySourceCol || !copyTargetCol}
            sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Copy Column</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={mergeDialogOpen} onClose={() => setMergeDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MergeIcon sx={{ color: PRIMARY }} /> Merge Rows
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }} color="text.secondary">
            Merge {selectedRows.length} selected rows into one. The first row will be kept and other rows' data will be merged into it.
          </Typography>
          <Alert severity="info">This action cannot be undone. Make sure to backup data before merging.</Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMergeDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleMergeRows} disabled={selectedRows.length < 2}
            sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Merge</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={syncDialogOpen} onClose={() => setSyncDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SyncIcon sx={{ color: PRIMARY }} /> Sync Data to Portal
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }} color="text.secondary">
            Sync data from <strong>{selectedDb?.name || selectedDb?.filename}</strong> to the <strong>{syncTarget}</strong> model.
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will map Access table columns to Django model fields. Please ensure the table structure matches the target model.
          </Alert>
          <Paper sx={{ p: 2, bgcolor: LAGOS_LIGHT }}>
            <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>Column Mapping Preview</Typography>
            <Typography variant="body2" color="text.secondary">
              Columns from the selected table will be automatically mapped to {syncTarget} model fields.
              Conflicting data will be overwritten.
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSyncDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSync} startIcon={<SyncIcon />}
            sx={{ bgcolor: PRIMARY, '&:hover': { bgcolor: PRIMARY_DARK } }}>Sync Now</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} variant="filled" sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default AccessDatabase
