import { render as rtlRender } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";

/**
 * Custom render function that includes common providers and setup
 */
export function render(ui: ReactElement, options = {}) {
  const user = userEvent.setup();

  return {
    user,
    ...rtlRender(ui, options),
  };
}

// Re-export everything from testing library
export * from "@testing-library/react";
export { userEvent };
