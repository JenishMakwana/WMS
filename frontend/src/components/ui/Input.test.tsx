import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Input } from "./Input";
import React from "react";

describe("Input", () => {
  it("renders with a label", () => {
    render(<Input label="Username" id="username" />);
    const label = screen.getByText("Username");
    const input = screen.getByRole("textbox");
    expect(label).toBeInTheDocument();
    expect(input).toBeInTheDocument();
  });

  it("handles user input", () => {
    const handleChange = vi.fn();
    render(<Input label="Email" onChange={handleChange} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "test@example.com" } });
    expect(handleChange).toHaveBeenCalledTimes(1);
    expect((input as HTMLInputElement).value).toBe("test@example.com");
  });

  it("displays an error message when error prop is provided", () => {
    render(<Input label="Password" error="Password is required" />);
    const errorText = screen.getByText("Password is required");
    expect(errorText).toBeInTheDocument();
  });

  it("applies error styling when error is present", () => {
    render(<Input label="Password" error="Error" />);
    // Check for border-red-500 class which indicates an error
    const inputContainer = screen.getByRole("textbox");
    expect(inputContainer.className).toContain("border-red-500");
  });

  it("forwards ref to the input element", () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input label="Ref Test" ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });
});
