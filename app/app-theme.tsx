"use client"

import { createTheme, ThemeProvider, CssBaseline } from "@mui/material"
import { ReactNode } from "react"

const lightTheme = createTheme({
  palette: {
    mode: "light", 
  },
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "white", // default (unfocused) border color
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "white", // hover state
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "#1976d2", // keep your primary color when focused
          },
        },
        input: {
          color: "white", // text color inside TextField
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: "white", // label color unfocused
          "&.Mui-focused": {
            color: "#1976d2", // primary color when focused
          },
        },
      },
    },
  },    
})

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline /> {/* resets default MUI styles */}
      {children}
    </ThemeProvider>
  )
}
