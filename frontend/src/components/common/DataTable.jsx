import React, { useState } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Checkbox,
  IconButton,
  Box,
  Typography,
  TextField,
  InputAdornment,
} from '@mui/material'
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material'

function DataTable({
  columns,
  data,
  onEdit,
  onDelete,
  onView,
  searchable = true,
  selectable = false,
  pageSize = 10,
}) {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(pageSize)
  const [order, setOrder] = useState('asc')
  const [orderBy, setOrderBy] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selected, setSelected] = useState([])

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(property)
  }

  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelected = data.map((n) => n.id)
      setSelected(newSelected)
      return
    }
    setSelected([])
  }

  const handleClick = (event, id) => {
    if (selectable) {
      const selectedIndex = selected.indexOf(id)
      let newSelected = []

      if (selectedIndex === -1) {
        newSelected = newSelected.concat(selected, id)
      } else if (selectedIndex === 0) {
        newSelected = newSelected.concat(selected.slice(1))
      } else if (selectedIndex === selected.length - 1) {
        newSelected = newSelected.concat(selected.slice(0, -1))
      } else if (selectedIndex > 0) {
        newSelected = newSelected.concat(
          selected.slice(0, selectedIndex),
          selected.slice(selectedIndex + 1)
        )
      }

      setSelected(newSelected)
    }
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const isSelected = (id) => selected.indexOf(id) !== -1

  // Filter and sort data
  const filteredData = data
    .filter((row) =>
      Object.values(row).some((value) =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    )
    .sort((a, b) => {
      if (orderBy) {
        const aVal = a[orderBy]
        const bVal = b[orderBy]
        if (order === 'asc') {
          return aVal < bVal ? -1 : 1
        }
        return aVal > bVal ? -1 : 1
      }
      return 0
    })

  const paginatedData = filteredData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {searchable && (
        <Box sx={{ p: 2 }}>
          <TextField
            size="small"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 300 }}
          />
        </Box>
      )}

      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selected.length > 0 && selected.length < data.length}
                    checked={data.length > 0 && selected.length === data.length}
                    onChange={handleSelectAllClick}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  sortDirection={orderBy === column.id ? order : false}
                  sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5' }}
                >
                  {column.sortable !== false ? (
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={() => handleRequestSort(column.id)}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
              {(onEdit || onDelete || onView) && (
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5' }}>
                  Actions
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (onEdit || onDelete || onView ? 1 : 0)}
                  align="center"
                  sx={{ py: 4 }}
                >
                  <Typography color="text.secondary">No data available</Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row) => {
                const isItemSelected = isSelected(row.id)
                return (
                  <TableRow
                    key={row.id}
                    hover
                    onClick={(event) => handleClick(event, row.id)}
                    role="checkbox"
                    aria-checked={isItemSelected}
                    selected={isItemSelected}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox checked={isItemSelected} />
                      </TableCell>
                    )}
                    {columns.map((column) => (
                      <TableCell key={column.id} align={column.align || 'left'}>
                        {column.render ? column.render(row) : row[column.id]}
                      </TableCell>
                    ))}
                    {(onEdit || onDelete || onView) && (
                      <TableCell align="right">
                        {onView && (
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              onView(row)
                            }}
                          >
                            <ViewIcon />
                          </IconButton>
                        )}
                        {onEdit && (
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              onEdit(row)
                            }}
                          >
                            <EditIcon />
                          </IconButton>
                        )}
                        {onDelete && (
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              onDelete(row)
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        )}
                      </TableCell>
                    )}
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={filteredData.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  )
}

export default DataTable
