import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import DataTable from '../../components/common/DataTable'

const columns = [
  { id: 'name', label: 'Name' },
  { id: 'email', label: 'Email' },
  { id: 'role', label: 'Role' },
]

const sampleData = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'Teacher' },
  { id: 3, name: 'Bob Wilson', email: 'bob@example.com', role: 'Student' },
]

function renderTable(overrides = {}) {
  const defaultProps = {
    columns,
    data: sampleData,
    ...overrides,
  }
  return render(<DataTable {...defaultProps} />)
}

describe('DataTable Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('rendering', () => {
    it('renders table headers', () => {
      renderTable()

      expect(screen.getByText('Name')).toBeInTheDocument()
      expect(screen.getByText('Email')).toBeInTheDocument()
      expect(screen.getByText('Role')).toBeInTheDocument()
    })

    it('renders table rows with data', () => {
      renderTable()

      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('john@example.com')).toBeInTheDocument()
      expect(screen.getByText('Admin')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.getByText('jane@example.com')).toBeInTheDocument()
    })

    it('renders "No data available" when data is empty', () => {
      renderTable({ data: [] })

      expect(screen.getByText('No data available')).toBeInTheDocument()
    })

    it('renders an actions column when callbacks are provided', () => {
      renderTable({ onEdit: vi.fn(), onDelete: vi.fn() })

      expect(screen.getByText('Actions')).toBeInTheDocument()
    })

    it('does not render actions column when no callbacks provided', () => {
      renderTable()

      expect(screen.queryByText('Actions')).not.toBeInTheDocument()
    })
  })

  describe('search functionality', () => {
    it('renders search input by default', () => {
      renderTable()

      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    })

    it('hides search input when searchable is false', () => {
      renderTable({ searchable: false })

      expect(screen.queryByPlaceholderText('Search...')).not.toBeInTheDocument()
    })

    it('filters data based on search term', () => {
      renderTable()

      const searchInput = screen.getByPlaceholderText('Search...')
      fireEvent.change(searchInput, { target: { value: 'Jane' } })

      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
      expect(screen.queryByText('John Doe')).not.toBeInTheDocument()
      expect(screen.queryByText('Bob Wilson')).not.toBeInTheDocument()
    })

    it('performs case-insensitive search', () => {
      renderTable()

      const searchInput = screen.getByPlaceholderText('Search...')
      fireEvent.change(searchInput, { target: { value: 'ADMIN' } })

      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    it('shows "No data available" when search yields no results', () => {
      renderTable()

      const searchInput = screen.getByPlaceholderText('Search...')
      fireEvent.change(searchInput, { target: { value: 'zzzznotfound' } })

      expect(screen.getByText('No data available')).toBeInTheDocument()
    })
  })

  describe('pagination', () => {
    const largeDataset = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      name: `User ${i + 1}`,
      email: `user${i + 1}@example.com`,
      role: 'Admin',
    }))

    it('renders pagination controls', () => {
      renderTable({ data: largeDataset })

      expect(screen.getByText('Rows per page:')).toBeInTheDocument()
      expect(screen.getByText('1–10 of 25')).toBeInTheDocument()
    })

    it('paginates data with default page size of 10', () => {
      renderTable({ data: largeDataset })

      expect(screen.getByText('User 1')).toBeInTheDocument()
      expect(screen.getByText('User 10')).toBeInTheDocument()
      expect(screen.queryByText('User 11')).not.toBeInTheDocument()
    })

    it('navigates to next page', () => {
      renderTable({ data: largeDataset })

      const nextButton = screen.getByRole('button', { name: /next page/i })
      fireEvent.click(nextButton)

      expect(screen.getByText('11–20 of 25')).toBeInTheDocument()
      expect(screen.getByText('User 11')).toBeInTheDocument()
    })

    it('navigates to previous page', () => {
      renderTable({ data: largeDataset })

      // Go to page 2 first
      const nextButton = screen.getByRole('button', { name: /next page/i })
      fireEvent.click(nextButton)

      // Now go back
      const prevButton = screen.getByRole('button', { name: /previous page/i })
      fireEvent.click(prevButton)

      expect(screen.getByText('1–10 of 25')).toBeInTheDocument()
    })

    it('respects custom pageSize prop', () => {
      renderTable({ data: largeDataset, pageSize: 5 })

      expect(screen.getByText('1–5 of 25')).toBeInTheDocument()
    })
  })

  describe('actions', () => {
    it('calls onEdit with row data when edit button is clicked', () => {
      const onEdit = vi.fn()
      renderTable({ onEdit })

      const editButtons = screen.getAllByRole('button').filter(
        (btn) => btn.querySelector('[data-testid="EditIcon"]')
      )
      fireEvent.click(editButtons[0])

      expect(onEdit).toHaveBeenCalledWith(sampleData[0])
    })

    it('calls onDelete with row data when delete button is clicked', () => {
      const onDelete = vi.fn()
      renderTable({ onDelete })

      const deleteButtons = screen.getAllByRole('button').filter(
        (btn) => btn.querySelector('[data-testid="DeleteIcon"]')
      )
      fireEvent.click(deleteButtons[0])

      expect(onDelete).toHaveBeenCalledWith(sampleData[0])
    })

    it('calls onView with row data when view button is clicked', () => {
      const onView = vi.fn()
      renderTable({ onView })

      const viewButtons = screen.getAllByRole('button').filter(
        (btn) => btn.querySelector('[data-testid="VisibilityIcon"]')
      )
      fireEvent.click(viewButtons[0])

      expect(onView).toHaveBeenCalledWith(sampleData[0])
    })

    it('does not render action buttons when no callbacks provided', () => {
      renderTable()

      const buttons = screen.getAllByRole('button').filter(
        (btn) => btn.querySelector('[data-testid="EditIcon"]') ||
                 btn.querySelector('[data-testid="DeleteIcon"]') ||
                 btn.querySelector('[data-testid="VisibilityIcon"]')
      )
      expect(buttons).toHaveLength(0)
    })
  })

  describe('custom column rendering', () => {
    it('uses custom render function for columns', () => {
      const customColumns = [
        { id: 'name', label: 'Name', render: (row) => <strong>{row.name}</strong> },
        { id: 'email', label: 'Email' },
      ]

      render(<DataTable columns={customColumns} data={sampleData} />)

      const strongElements = screen.getAllByText((content, element) => {
        return element?.tagName === 'STRONG' && content === 'John Doe'
      })
      expect(strongElements.length).toBeGreaterThan(0)
    })
  })

  describe('selectable mode', () => {
    it('renders checkboxes when selectable is true', () => {
      renderTable({ selectable: true })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBeGreaterThanOrEqual(1)
    })

    it('renders fewer or no checkboxes when selectable is false', () => {
      renderTable({ selectable: false })
      const checkboxesWithSelection = screen.queryAllByRole('checkbox')
      renderTable({ selectable: true })
      const checkboxesWithSelectionTrue = screen.getAllByRole('checkbox')
      expect(checkboxesWithSelection.length).toBeLessThan(checkboxesWithSelectionTrue.length)
    })
  })
})
