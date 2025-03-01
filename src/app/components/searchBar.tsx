"use client"; // Ensure this is a client component
import React from 'react';
import { useState } from "react";
import { Button } from "antd";

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <div className="flex gap-2">
      <input
        type="text"
        placeholder="Search for a plant..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{ color: "black" }}
        className="border p-2 rounded w-full"
      />
      <Button 
        onClick={handleSearch}
        className="ant-btn-primary"
      >
        Search
      </Button>
    </div>
  );
}
