import React from 'react';

export interface SearchProps {
  placeholder?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const Search: React.FC<SearchProps> = ({ placeholder = '', onChange }) => (
  <input
    type="text"
    className="border rounded px-2 py-1 w-full"
    placeholder={placeholder}
    onChange={onChange}
  />
);
