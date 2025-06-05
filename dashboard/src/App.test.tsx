import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Trading Fund heading', () => {
  render(<App />);
  const heading = screen.getByRole('heading', { name: /Trading Fund/i });
  expect(heading).toBeInTheDocument();
});
