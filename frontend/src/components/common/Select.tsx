import React, { forwardRef } from 'react'

interface Option {
  value: string
  label: string
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: Option[]
  error?: string
  helpText?: string
  placeholder?: string
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(({
  label,
  options,
  error,
  helpText,
  placeholder = 'Select an option',
  className = '',
  id,
  ...props
}, ref) => {
  const selectId = id || label?.toLowerCase().replace(/\s+/g, '-')
  
  const selectClasses = `
    block w-full rounded-md shadow-sm sm:text-sm
    ${error 
      ? 'border-red-300 text-red-900 focus:border-red-500 focus:ring-red-500' 
      : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500'
    }
    ${props.disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : ''}
  `.trim()

  return (
    <div className={className}>
      {label && (
        <label 
          htmlFor={selectId} 
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      
      <select
        ref={ref}
        id={selectId}
        className={selectClasses}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
      
      {helpText && !error && (
        <p className="mt-1 text-sm text-gray-500">
          {helpText}
        </p>
      )}
    </div>
  )
})

Select.displayName = 'Select'

export default Select