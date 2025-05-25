import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a custom render that includes providers
const customRender = (ui, options = {}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>,
    options
  );
};

// Re-export everything
export * from '@testing-library/react';
// Override render method
export { customRender as render };
